import os
import uuid
import zipfile
import rarfile
from PIL import Image
from werkzeug.utils import secure_filename
from datetime import datetime
import io
import mimetypes
import logging

class FileManager:
    def __init__(self, app):
        self.app = app
        self.upload_folder = 'uploads'
        self.notes_folder = os.path.join(self.upload_folder, 'notes')
        self.projects_folder = os.path.join(self.upload_folder, 'projects')
        self.temp_folder = os.path.join(self.upload_folder, 'temp')
        self.questions_folder = os.path.join(self.upload_folder, 'questions')
        
        # Logger setup - basit formatter kullan
        self.logger = logging.getLogger('file_upload')
        # Eğer handler yoksa ekle
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Desteklenen dosya türleri
        self.allowed_extensions = {
            'notes': {'pdf', 'docx', 'png', 'jpg', 'jpeg', 'gif', 'bmp'},
            'projects': {'zip', 'rar', 'pdf', 'docx', 'txt', 'py', 'cpp', 'h', 'ino'},
            'questions': {'pdf', 'png'}
        }
        
        # Maksimum dosya boyutları (MB)
        self.max_file_sizes = {
            'notes': 50,  # 50MB
            'projects': 100,  # 100MB
            'questions': 100
        }
        
        # Klasörleri oluştur
        self._create_folders()
    
    def _create_folders(self):
        """Gerekli klasörleri oluştur"""
        for folder in [self.upload_folder, self.notes_folder, self.projects_folder, self.questions_folder, self.temp_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
    
    def is_allowed_file(self, filename, file_type):
        """Dosya türünün desteklenip desteklenmediğini kontrol et"""
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in self.allowed_extensions.get(file_type, set())
    
    def validate_file_size(self, file, file_type):
        """Dosya boyutunu kontrol et"""
        max_size = self.max_file_sizes.get(file_type, 10) * 1024 * 1024  # MB to bytes
        return file.content_length <= max_size if hasattr(file, 'content_length') else True
    
    def validate_file_content(self, file_path, file_type):
        """Dosya içeriğini güvenlik açısından kontrol et"""
        try:
            # Dosya uzantısından MIME türünü tahmin et
            mime_type, _ = mimetypes.guess_type(file_path)
            
            # Güvenli MIME türleri
            safe_mimes = {
                'notes': ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'image/png', 'image/jpeg', 'image/gif', 'image/bmp'],
                'projects': ['application/zip', 'application/x-rar-compressed', 'application/pdf',
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'text/plain', 'text/x-python', 'text/x-c++src', 'text/x-arduino'],
                'questions': ['application/pdf', 'image/png']
            }
            
            # Dosya uzantısı kontrolü
            file_ext = os.path.splitext(file_path)[1].lower()
            safe_extensions = {
                'notes': {'.pdf', '.docx', '.png', '.jpg', '.jpeg', '.gif', '.bmp'},
                'projects': {'.zip', '.rar', '.pdf', '.docx', '.txt', '.py', '.cpp', '.h', '.ino'},
                'questions': {'.pdf', '.png'}
            }
            
            if file_ext not in safe_extensions.get(file_type, set()):
                return False, f"Güvenli olmayan dosya uzantısı: {file_ext}"
            
            # MIME türü kontrolü (eğer tahmin edilebiliyorsa)
            if mime_type and mime_type not in safe_mimes.get(file_type, []):
                return False, f"Güvenli olmayan dosya türü: {mime_type}"
            
            return True, "Dosya güvenli"
            
        except Exception as e:
            return False, f"Dosya doğrulama hatası: {str(e)}"
    
    def generate_unique_filename(self, original_filename, file_type):
        """Benzersiz dosya adı oluştur"""
        ext = original_filename.rsplit('.', 1)[1].lower()
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{file_type}_{timestamp}_{unique_id}.{ext}"
    
    def save_file(self, file, file_type, user_id):
        """Dosyayı güvenli şekilde kaydet"""
        try:
            if not file or file.filename == '':
                self.logger.warning(f"No file selected for upload - User: {user_id}")
                return None, "Dosya seçilmedi"
            
            self.logger.info(f"File upload attempt: {file.filename} - Type: {file_type} - User: {user_id}")
            
            if not self.is_allowed_file(file.filename, file_type):
                self.logger.warning(f"Unsupported file type: {file.filename} - User: {user_id}")
                return None, f"Desteklenmeyen dosya türü: {file.filename}"
            
            if not self.validate_file_size(file, file_type):
                max_size = self.max_file_sizes.get(file_type, 10)
                self.logger.warning(f"File too large: {file.filename} - User: {user_id} - Max size: {max_size}MB")
                return None, f"Dosya boyutu çok büyük. Maksimum: {max_size}MB"
            
            # Güvenli dosya adı oluştur
            filename = secure_filename(file.filename)
            unique_filename = self.generate_unique_filename(filename, file_type)
            
            # Dosya türüne göre klasör seç
            if file_type == 'notes':
                save_path = os.path.join(self.notes_folder, unique_filename)
            elif file_type == 'projects':
                save_path = os.path.join(self.projects_folder, unique_filename)
            elif file_type == 'questions':
                save_path = os.path.join(self.questions_folder, unique_filename)
            else:
                self.logger.error(f"Invalid file type: {file_type} - User: {user_id}")
                return None, "Geçersiz dosya türü"
            
            # Dosyayı kaydet
            file.save(save_path)
            self.logger.info(f"File saved to disk: {save_path} - User: {user_id}")
            
            # Dosya içeriğini doğrula
            is_safe, message = self.validate_file_content(save_path, file_type)
            if not is_safe:
                # Güvenli olmayan dosyayı sil
                os.remove(save_path)
                self.logger.error(f"Unsafe file detected and removed: {save_path} - User: {user_id} - Reason: {message}")
                return None, message
            
            file_size = os.path.getsize(save_path)
            self.logger.info(f"File upload successful: {filename} -> {unique_filename} - Size: {file_size} bytes - User: {user_id}")
            
            # URL için kullanılacak dosya adını da döndür
            return {
                'original_name': filename,
                'saved_name': unique_filename,
                'file_path': unique_filename,  # Sadece dosya adı (klasör yolu olmadan)
                'file_url': unique_filename,  # URL için sadece dosya adı
                'file_size': file_size,
                'file_type': file_type,
                'upload_date': datetime.now(),
                'user_id': user_id
            }, "Dosya başarıyla yüklendi"
            
        except Exception as e:
            self.logger.error(f"File save error: {str(e)} - User: {user_id} - File: {file.filename if file else 'Unknown'}")
            return None, f"Dosya kaydetme hatası: {str(e)}"
    
    def extract_archive_info(self, file_path):
        """Arşiv dosyalarından bilgi çıkar"""
        try:
            if file_path.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    return {
                        'type': 'zip',
                        'file_count': len(file_list),
                        'files': file_list[:10],  # İlk 10 dosya
                        'total_size': sum(zip_file.getinfo(f).file_size for f in file_list)
                    }
            elif file_path.endswith('.rar'):
                with rarfile.RarFile(file_path, 'r') as rar_file:
                    file_list = rar_file.namelist()
                    return {
                        'type': 'rar',
                        'file_count': len(file_list),
                        'files': file_list[:10],  # İlk 10 dosya
                        'total_size': sum(rar_file.getinfo(f).file_size for f in file_list)
                    }
        except Exception as e:
            return {'error': str(e)}
        
        return None
    

    
    def delete_file(self, file_path):
        """Dosyayı sil"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True, "Dosya başarıyla silindi"
            return False, "Dosya bulunamadı"
        except Exception as e:
            return False, f"Dosya silme hatası: {str(e)}"
    
    def get_file_info(self, file_path):
        """Dosya bilgilerini getir"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'mime_type': mime_type or 'application/octet-stream'
            }
        except Exception as e:
            return None
