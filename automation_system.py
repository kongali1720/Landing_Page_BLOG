import os
import shutil
import smtplib
import schedule
import time
import requests
import csv
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

class FileOrganizer:
    """Automated file organization system"""
    
    def __init__(self, source_dir: str, organized_dir: str):
        self.source_dir = Path(source_dir)
        self.organized_dir = Path(organized_dir)
        self.organized_dir.mkdir(exist_ok=True)
        
        # File type mappings
        self.file_types = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'Presentations': ['.ppt', '.pptx', '.odp'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php']
        }
    
    def organize_files(self):
        """Organize files from source directory into categorized folders"""
        if not self.source_dir.exists():
            logging.error(f"Source directory {self.source_dir} does not exist")
            return
        
        organized_count = 0
        
        for file_path in self.source_dir.iterdir():
            if file_path.is_file():
                file_extension = file_path.suffix.lower()
                category = self.get_file_category(file_extension)
                
                # Create category folder if it doesn't exist
                category_folder = self.organized_dir / category
                category_folder.mkdir(exist_ok=True)
                
                # Move file to appropriate category
                destination = category_folder / file_path.name
                
                # Handle duplicate names
                counter = 1
                while destination.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    destination = category_folder / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                try:
                    shutil.move(str(file_path), str(destination))
                    logging.info(f"Moved {file_path.name} to {category}")
                    organized_count += 1
                except Exception as e:
                    logging.error(f"Error moving {file_path.name}: {e}")
        
        logging.info(f"Organized {organized_count} files")
        return organized_count
    
    def get_file_category(self, extension: str) -> str:
        """Determine file category based on extension"""
        for category, extensions in self.file_types.items():
            if extension in extensions:
                return category
        return 'Other'
    
    def clean_empty_folders(self, directory: Path = None):
        """Remove empty folders from directory"""
        if directory is None:
            directory = self.organized_dir
        
        for folder in directory.iterdir():
            if folder.is_dir():
                self.clean_empty_folders(folder)
                try:
                    if not any(folder.iterdir()):
                        folder.rmdir()
                        logging.info(f"Removed empty folder: {folder}")
                except OSError:
                    pass

class BackupManager:
    """Automated backup system"""
    
    def __init__(self, source_dirs: List[str], backup_dir: str):
        self.source_dirs = [Path(d) for d in source_dirs]
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, include_timestamp: bool = True):
        """Create backup of specified directories"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        backup_success = []
        
        for source_dir in self.source_dirs:
            if not source_dir.exists():
                logging.warning(f"Source directory {source_dir} does not exist")
                continue
            
            backup_name = f"{source_dir.name}_{timestamp}" if timestamp else source_dir.name
            backup_path = self.backup_dir / backup_name
            
            try:
                shutil.copytree(source_dir, backup_path, dirs_exist_ok=True)
                logging.info(f"Backup created: {backup_path}")
                backup_success.append(str(backup_path))
            except Exception as e:
                logging.error(f"Backup failed for {source_dir}: {e}")
        
        return backup_success
    
    def cleanup_old_backups(self, days_to_keep: int = 30):
        """Remove backups older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        removed_count = 0
        
        for backup_folder in self.backup_dir.iterdir():
            if backup_folder.is_dir():
                folder_time = datetime.fromtimestamp(backup_folder.stat().st_mtime)
                if folder_time < cutoff_date:
                    try:
                        shutil.rmtree(backup_folder)
                        logging.info(f"Removed old backup: {backup_folder}")
                        removed_count += 1
                    except Exception as e:
                        logging.error(f"Error removing {backup_folder}: {e}")
        
        logging.info(f"Removed {removed_count} old backups")
        return removed_count

class EmailAutomation:
    """Automated email sending system"""
    
    def __init__(self, smtp_server: str, smtp_port: int, email: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   attachments: Optional[List[str]] = None):
        """Send email with optional attachments"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            text = msg.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()
            
            logging.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False
    
    def send_backup_report(self, to_email: str, backup_paths: List[str]):
        """Send backup completion report"""
        subject = f"Backup Report - {datetime.now().strftime('%Y-%m-%d')}"
        body = f"""
        Backup Report
        =============
        
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Backup Status: {'Success' if backup_paths else 'Failed'}
        Number of backups created: {len(backup_paths)}
        
        Backup Locations:
        {chr(10).join(f'• {path}' for path in backup_paths)}
        
        This is an automated message from your backup system.
        """
        
        return self.send_email(to_email, subject, body)

class WebMonitor:
    """Website monitoring and alerting system"""
    
    def __init__(self, websites: List[Dict[str, str]]):
        self.websites = websites  # [{'name': 'Site Name', 'url': 'https://...'}]
        self.status_file = 'website_status.json'
    
    def check_website(self, url: str, timeout: int = 10) -> Dict:
        """Check if website is accessible"""
        try:
            response = requests.get(url, timeout=timeout)
            return {
                'status': 'UP',
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
        except requests.RequestException as e:
            return {
                'status': 'DOWN',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def monitor_websites(self) -> Dict[str, Dict]:
        """Monitor all configured websites"""
        results = {}
        
        for site in self.websites:
            name = site['name']
            url = site['url']
            
            logging.info(f"Checking {name} ({url})")
            result = self.check_website(url)
            results[name] = result
            
            if result['status'] == 'UP':
                logging.info(f"{name} is UP (Response time: {result.get('response_time', 'N/A')}s)")
            else:
                logging.warning(f"{name} is DOWN - {result.get('error', 'Unknown error')}")
        
        # Save status to file
        self.save_status(results)
        return results
    
    def save_status(self, status: Dict):
        """Save website status to file"""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving status: {e}")
    
    def load_previous_status(self) -> Dict:
        """Load previous website status"""
        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            logging.error(f"Error loading status: {e}")
            return {}

class AutomationScheduler:
    """Main automation scheduler"""
    
    def __init__(self):
        self.file_organizer = None
        self.backup_manager = None
        self.email_automation = None
        self.web_monitor = None
    
    def setup_file_organizer(self, source_dir: str, organized_dir: str):
        """Setup file organization automation"""
        self.file_organizer = FileOrganizer(source_dir, organized_dir)
    
    def setup_backup_manager(self, source_dirs: List[str], backup_dir: str):
        """Setup backup automation"""
        self.backup_manager = BackupManager(source_dirs, backup_dir)
    
    def setup_email_automation(self, smtp_server: str, smtp_port: int, 
                             email: str, password: str):
        """Setup email automation"""
        self.email_automation = EmailAutomation(smtp_server, smtp_port, email, password)
    
    def setup_web_monitor(self, websites: List[Dict[str, str]]):
        """Setup website monitoring"""
        self.web_monitor = WebMonitor(websites)
    
    def run_file_organization(self):
        """Run file organization task"""
        if self.file_organizer:
            logging.info("Starting file organization...")
            count = self.file_organizer.organize_files()
            self.file_organizer.clean_empty_folders()
            return count
        return 0
    
    def run_backup_task(self):
        """Run backup task"""
        if self.backup_manager:
            logging.info("Starting backup task...")
            backup_paths = self.backup_manager.create_backup()
            self.backup_manager.cleanup_old_backups()
            
            # Send email report if email is configured
            if self.email_automation and backup_paths:
                self.email_automation.send_backup_report(
                    "admin@example.com",  # Configure recipient
                    backup_paths
                )
            
            return backup_paths
        return []
    
    def run_website_monitoring(self):
        """Run website monitoring task"""
        if self.web_monitor:
            logging.info("Starting website monitoring...")
            return self.web_monitor.monitor_websites()
        return {}
    
    def schedule_tasks(self):
        """Schedule all automation tasks"""
        # Schedule file organization every day at 2 AM
        schedule.every().day.at("02:00").do(self.run_file_organization)
        
        # Schedule backup every Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(self.run_backup_task)
        
        # Schedule website monitoring every 30 minutes
        schedule.every(30).minutes.do(self.run_website_monitoring)
        
        logging.info("Automation tasks scheduled successfully")
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        logging.info("Starting automation scheduler...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Example usage and configuration
def main():
    """Main function demonstrating automation setup"""
    
    # Initialize automation scheduler
    scheduler = AutomationScheduler()
    
    # Configure file organization
    scheduler.setup_file_organizer(
        source_dir="/Users/username/Downloads",  # Customize path
        organized_dir="/Users/username/Organized"
    )
    
    # Configure backup system
    scheduler.setup_backup_manager(
        source_dirs=["/Users/username/Documents", "/Users/username/Projects"],
        backup_dir="/Users/username/Backups"
    )
    
    # Configure email automation (use app passwords for Gmail)
    scheduler.setup_email_automation(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        email="your-email@gmail.com",
        password="your-app-password"
    )
    
    # Configure website monitoring
    websites_to_monitor = [
        {"name": "My Website", "url": "https://mywebsite.com"},
        {"name": "API Service", "url": "https://api.myservice.com/health"},
        {"name": "Blog", "url": "https://myblog.com"}
    ]
    scheduler.setup_web_monitor(websites_to_monitor)
    
    # Schedule tasks
    scheduler.schedule_tasks()
    
    # Run manual tasks for testing
    print("Running manual tests...")
    scheduler.run_file_organization()
    scheduler.run_website_monitoring()
    
    # Start scheduler (comment out for manual testing)
    # scheduler.run_scheduler()

if __name__ == "__main__":
    main()

# Additional standalone automation functions

def bulk_file_rename(directory: str, pattern: str, replacement: str):
    """Bulk rename files matching a pattern"""
    path = Path(directory)
    renamed_count = 0
    
    for file_path in path.glob(pattern):
        if file_path.is_file():
            new_name = file_path.name.replace(pattern.replace('*', ''), replacement)
            new_path = file_path.parent / new_name
            
            try:
                file_path.rename(new_path)
                logging.info(f"Renamed {file_path.name} to {new_name}")
                renamed_count += 1
            except Exception as e:
                logging.error(f"Error renaming {file_path.name}: {e}")
    
    return renamed_count

def generate_system_report():
    """Generate system resource usage report"""
    import psutil
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'free': psutil.disk_usage('/').free,
            'percent': psutil.disk_usage('/').percent
        }
    }
    
    # Save to CSV for historical tracking
    csv_file = 'system_report.csv'
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'cpu_percent', 'memory_percent', 'disk_percent'])
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'timestamp': report['timestamp'],
            'cpu_percent': report['cpu_percent'],
            'memory_percent': report['memory']['percent'],
            'disk_percent': report['disk']['percent']
        })
    
    return report

# Installation requirements:
"""
pip install schedule requests psutil

For email functionality, you may need to:
1. Enable 2-factor authentication on Gmail
2. Generate an app password
3. Use the app password instead of your regular password
"""

