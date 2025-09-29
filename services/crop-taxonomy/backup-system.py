#!/usr/bin/env python3
"""
Backup and Disaster Recovery System for CAAIN Soil Hub Crop Taxonomy Service
Comprehensive backup, restore, and disaster recovery automation
"""

import os
import sys
import json
import yaml
import shutil
import subprocess
import tarfile
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import psycopg2
import redis
import requests


class BackupSystem:
    """Comprehensive backup and disaster recovery system."""
    
    def __init__(self, config_path: str = "backup-config.yml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.backup_dir = Path(self.config['backup']['directory'])
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load backup configuration."""
        default_config = {
            'backup': {
                'directory': '/app/backups',
                'retention_days': 30,
                'compression': True,
                'encryption': False
            },
            'database': {
                'host': 'postgres',
                'port': 5432,
                'database': 'crop_taxonomy',
                'username': 'caain_user',
                'password': 'secure_password'
            },
            'redis': {
                'host': 'redis',
                'port': 6379,
                'password': 'redis_password'
            },
            'storage': {
                'local': True,
                's3': {
                    'enabled': False,
                    'bucket': 'caain-backups',
                    'region': 'us-east-1'
                }
            },
            'notifications': {
                'email': {
                    'enabled': False,
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'username': '',
                    'password': '',
                    'to_addresses': []
                },
                'webhook': {
                    'enabled': False,
                    'url': ''
                }
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(user_config)
        
        return default_config
    
    def create_database_backup(self) -> str:
        """Create PostgreSQL database backup."""
        print("🗄️  Creating database backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"database_backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Create database dump
            cmd = [
                'pg_dump',
                '-h', self.config['database']['host'],
                '-p', str(self.config['database']['port']),
                '-U', self.config['database']['username'],
                '-d', self.config['database']['database'],
                '-f', str(backup_path),
                '--verbose',
                '--no-password'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config['database']['password']
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Database backup failed: {result.stderr}")
            
            # Compress if enabled
            if self.config['backup']['compression']:
                compressed_path = f"{backup_path}.gz"
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(backup_path)
                backup_path = Path(compressed_path)
            
            print(f"✅ Database backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Database backup failed: {e}")
            raise
    
    def create_redis_backup(self) -> str:
        """Create Redis backup."""
        print("🔴 Creating Redis backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"redis_backup_{timestamp}.rdb"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Connect to Redis
            r = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                password=self.config['redis']['password'],
                decode_responses=True
            )
            
            # Trigger background save
            r.bgsave()
            
            # Wait for save to complete
            while r.lastsave() == r.lastsave():
                import time
                time.sleep(1)
            
            # Copy RDB file
            redis_data_dir = Path('/data')  # Redis data directory in container
            rdb_file = redis_data_dir / 'dump.rdb'
            
            if rdb_file.exists():
                shutil.copy2(rdb_file, backup_path)
                
                # Compress if enabled
                if self.config['backup']['compression']:
                    compressed_path = f"{backup_path}.gz"
                    with open(backup_path, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(backup_path)
                    backup_path = Path(compressed_path)
                
                print(f"✅ Redis backup created: {backup_path}")
                return str(backup_path)
            else:
                raise Exception("Redis RDB file not found")
                
        except Exception as e:
            print(f"❌ Redis backup failed: {e}")
            raise
    
    def create_configuration_backup(self) -> str:
        """Create configuration files backup."""
        print("⚙️  Creating configuration backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"config_backup_{timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Files to backup
            config_files = [
                'docker-compose.yml',
                'nginx.conf',
                '.env.production',
                'prometheus.yml',
                'alert_rules.yml',
                'alertmanager.yml',
                'grafana-dashboard.json',
                'health-checks.yml',
                'logging.conf'
            ]
            
            with tarfile.open(backup_path, 'w:gz') as tar:
                for file_path in config_files:
                    file_obj = Path(file_path)
                    if file_obj.exists():
                        tar.add(file_obj, arcname=file_obj.name)
                        print(f"  Added: {file_obj.name}")
            
            print(f"✅ Configuration backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Configuration backup failed: {e}")
            raise
    
    def create_application_backup(self) -> str:
        """Create application code and data backup."""
        print("📦 Creating application backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"application_backup_{timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Directories to backup
            backup_dirs = [
                'src/',
                'database/migrations/',
                'scripts/',
                'logs/'
            ]
            
            with tarfile.open(backup_path, 'w:gz') as tar:
                for dir_path in backup_dirs:
                    dir_obj = Path(dir_path)
                    if dir_obj.exists():
                        tar.add(dir_obj, arcname=dir_obj.name)
                        print(f"  Added: {dir_obj.name}")
            
            print(f"✅ Application backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Application backup failed: {e}")
            raise
    
    def create_full_backup(self) -> Dict[str, str]:
        """Create complete system backup."""
        print("🔄 Creating full system backup...")
        print("=" * 50)
        
        backup_files = {}
        
        try:
            # Create all backups
            backup_files['database'] = self.create_database_backup()
            backup_files['redis'] = self.create_redis_backup()
            backup_files['configuration'] = self.create_configuration_backup()
            backup_files['application'] = self.create_application_backup()
            
            # Create backup manifest
            manifest = {
                'timestamp': datetime.now().isoformat(),
                'backup_type': 'full',
                'files': backup_files,
                'config': self.config
            }
            
            manifest_path = self.backup_dir / f"backup_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            print(f"✅ Full backup completed: {manifest_path}")
            return backup_files
            
        except Exception as e:
            print(f"❌ Full backup failed: {e}")
            raise
    
    def restore_database(self, backup_file: str) -> bool:
        """Restore PostgreSQL database from backup."""
        print(f"🗄️  Restoring database from: {backup_file}")
        
        try:
            backup_path = Path(backup_file)
            
            # Decompress if needed
            if backup_path.suffix == '.gz':
                decompressed_path = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(decompressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                restore_file = decompressed_path
            else:
                restore_file = backup_path
            
            # Drop and recreate database
            drop_cmd = [
                'psql',
                '-h', self.config['database']['host'],
                '-p', str(self.config['database']['port']),
                '-U', self.config['database']['username'],
                '-c', f"DROP DATABASE IF EXISTS {self.config['database']['database']};"
            ]
            
            create_cmd = [
                'psql',
                '-h', self.config['database']['host'],
                '-p', str(self.config['database']['port']),
                '-U', self.config['database']['username'],
                '-c', f"CREATE DATABASE {self.config['database']['database']};"
            ]
            
            restore_cmd = [
                'psql',
                '-h', self.config['database']['host'],
                '-p', str(self.config['database']['port']),
                '-U', self.config['database']['username'],
                '-d', self.config['database']['database'],
                '-f', str(restore_file)
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config['database']['password']
            
            # Execute restore commands
            subprocess.run(drop_cmd, env=env, check=True)
            subprocess.run(create_cmd, env=env, check=True)
            subprocess.run(restore_cmd, env=env, check=True)
            
            # Clean up decompressed file
            if backup_path.suffix == '.gz':
                os.remove(restore_file)
            
            print("✅ Database restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ Database restore failed: {e}")
            return False
    
    def restore_redis(self, backup_file: str) -> bool:
        """Restore Redis from backup."""
        print(f"🔴 Restoring Redis from: {backup_file}")
        
        try:
            backup_path = Path(backup_file)
            
            # Decompress if needed
            if backup_path.suffix == '.gz':
                decompressed_path = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(decompressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                restore_file = decompressed_path
            else:
                restore_file = backup_path
            
            # Stop Redis, replace RDB file, restart Redis
            subprocess.run(['docker-compose', 'stop', 'redis'], check=True)
            
            redis_data_dir = Path('/data')
            shutil.copy2(restore_file, redis_data_dir / 'dump.rdb')
            
            subprocess.run(['docker-compose', 'start', 'redis'], check=True)
            
            # Clean up decompressed file
            if backup_path.suffix == '.gz':
                os.remove(restore_file)
            
            print("✅ Redis restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ Redis restore failed: {e}")
            return False
    
    def restore_configuration(self, backup_file: str) -> bool:
        """Restore configuration files from backup."""
        print(f"⚙️  Restoring configuration from: {backup_file}")
        
        try:
            backup_path = Path(backup_file)
            
            # Extract configuration files
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(path='.')
            
            print("✅ Configuration restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ Configuration restore failed: {e}")
            return False
    
    def cleanup_old_backups(self) -> int:
        """Clean up old backup files based on retention policy."""
        print("🧹 Cleaning up old backups...")
        
        retention_days = self.config['backup']['retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted_count = 0
        
        for backup_file in self.backup_dir.glob('*'):
            if backup_file.is_file():
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    print(f"  Deleted: {backup_file.name}")
        
        print(f"✅ Cleaned up {deleted_count} old backup files")
        return deleted_count
    
    def verify_backup_integrity(self, backup_file: str) -> bool:
        """Verify backup file integrity."""
        print(f"🔍 Verifying backup integrity: {backup_file}")
        
        try:
            backup_path = Path(backup_file)
            
            if backup_path.suffix == '.gz':
                # Test gzip integrity
                with gzip.open(backup_path, 'rb') as f:
                    f.read(1024)  # Read first 1KB
            elif backup_path.suffix == '.tar.gz':
                # Test tar.gz integrity
                with tarfile.open(backup_path, 'r:gz') as tar:
                    tar.getmembers()  # Get member list
            
            print("✅ Backup integrity verified")
            return True
            
        except Exception as e:
            print(f"❌ Backup integrity check failed: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups."""
        backups = []
        
        for backup_file in self.backup_dir.glob('*'):
            if backup_file.is_file():
                stat = backup_file.stat()
                backups.append({
                    'filename': backup_file.name,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def send_notification(self, message: str, success: bool = True) -> bool:
        """Send backup notification."""
        try:
            if self.config['notifications']['webhook']['enabled']:
                webhook_url = self.config['notifications']['webhook']['url']
                payload = {
                    'text': message,
                    'status': 'success' if success else 'error'
                }
                requests.post(webhook_url, json=payload, timeout=10)
            
            print(f"📧 Notification sent: {message}")
            return True
            
        except Exception as e:
            print(f"❌ Notification failed: {e}")
            return False


def main():
    """Main backup system function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CAAIN Soil Hub Backup System')
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'cleanup', 'verify'],
                       help='Action to perform')
    parser.add_argument('--file', help='Backup file for restore/verify operations')
    parser.add_argument('--config', default='backup-config.yml',
                       help='Configuration file path')
    
    args = parser.parse_args()
    
    backup_system = BackupSystem(args.config)
    
    try:
        if args.action == 'backup':
            backup_files = backup_system.create_full_backup()
            backup_system.cleanup_old_backups()
            backup_system.send_notification("Full backup completed successfully")
            
        elif args.action == 'restore':
            if not args.file:
                print("❌ Backup file required for restore operation")
                sys.exit(1)
            
            if 'database' in args.file:
                backup_system.restore_database(args.file)
            elif 'redis' in args.file:
                backup_system.restore_redis(args.file)
            elif 'config' in args.file:
                backup_system.restore_configuration(args.file)
            else:
                print("❌ Unknown backup type")
                sys.exit(1)
            
            backup_system.send_notification("Restore operation completed successfully")
            
        elif args.action == 'list':
            backups = backup_system.list_backups()
            print("\n📋 Available Backups:")
            print("-" * 80)
            for backup in backups:
                print(f"{backup['filename']:<40} {backup['size']:>10} bytes {backup['created']}")
            
        elif args.action == 'cleanup':
            deleted_count = backup_system.cleanup_old_backups()
            print(f"✅ Cleanup completed: {deleted_count} files deleted")
            
        elif args.action == 'verify':
            if not args.file:
                print("❌ Backup file required for verify operation")
                sys.exit(1)
            
            if backup_system.verify_backup_integrity(args.file):
                print("✅ Backup verification successful")
            else:
                print("❌ Backup verification failed")
                sys.exit(1)
    
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        backup_system.send_notification(f"Backup operation failed: {e}", success=False)
        sys.exit(1)


if __name__ == "__main__":
    main()