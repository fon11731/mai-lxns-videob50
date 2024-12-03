from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import webbrowser
import os
from urllib.parse import parse_qs
import threading

class ConfigHandler(SimpleHTTPRequestHandler):
    config_file = None  # Class variable to store config file path
    image_output_path = None  # Class variable to store image path
    video_download_path = None  # Class variable to store video path
    username = None  # Class variable to store username

    def do_GET(self):
        if self.path == '/':
            # Get the front_end directory path
            front_end_dir = os.path.dirname(os.path.abspath(__file__))
            editor_path = os.path.join(front_end_dir, 'editor.html')
            
            # Serve the main HTML page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(editor_path, 'rb') as f:
                self.wfile.write(f.read())
        
        elif self.path == '/config':
            if not self.config_file or not os.path.exists(self.config_file):
                self.send_error(404, "Config file not found")
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            with open(self.config_file, 'rb') as f:
                self.wfile.write(f.read())
        
        elif self.path == '/username':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(self.username.encode())

        elif self.path.startswith('/images/'):
            image_name = self.path.split('/')[-1]
            image_path = os.path.join(self.image_output_path, image_name)
            if os.path.exists(image_path):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(image_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Image not found")
        
        elif self.path.startswith('/asset/images/'):
            image_name = self.path.split('/')[-1]
            image_path = os.path.join("./images", image_name)
            if os.path.exists(image_path):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(image_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Placeholder Image not found")

        elif self.path.startswith('/videos/'):
            video_name = self.path.split('/')[-1]
            video_path = os.path.join(self.video_download_path, video_name)
            
            if not os.path.exists(video_path):
                self.send_error(404, "Video not found")
                return

            # 获取文件大小
            file_size = os.path.getsize(video_path)
            
            # 处理范围请求
            range_header = self.headers.get('Range')
            
            if range_header:
                try:
                    # 解析Range头
                    bytes_range = range_header.replace('bytes=', '').split('-')
                    start = int(bytes_range[0])
                    end = int(bytes_range[1]) if bytes_range[1] else file_size - 1
                    
                    # 确保范围有效
                    if start >= file_size:
                        self.send_error(416, "Requested range not satisfiable")
                        return
                    
                    # 发送部分内容响应
                    self.send_response(206)
                    self.send_header('Content-Type', 'video/mp4')
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                    self.send_header('Content-Length', str(end - start + 1))
                    self.end_headers()
                    
                    # 发送请求的范围内容
                    with open(video_path, 'rb') as f:
                        f.seek(start)
                        self.wfile.write(f.read(end - start + 1))
                        
                except Exception as e:
                    print(f"Error handling range request: {e}")
                    self.send_error(500, "Internal server error")
            else:
                # 发送完整文件
                self.send_response(200)
                self.send_header('Content-Type', 'video/mp4')
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Length', str(file_size))
                self.end_headers()
                
                with open(video_path, 'rb') as f:
                    self.wfile.write(f.read())

    def do_POST(self):
        if self.path == '/save':
            if not self.config_file:
                self.send_error(404, "Config file not specified")
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            updated_config = json.loads(post_data.decode('utf-8'))
            
            # Save the updated config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(updated_config, f, ensure_ascii=False, indent=4)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())

    def log_message(self, format, *args):
        # 只记录错误状态码（4xx 和 5xx）
        if len(args) >= 3 and (args[1].startswith('4') or args[1].startswith('5')):
            super().log_message(format, *args)

def run_server(config_file, image_output_path, video_download_path, username):
    ConfigHandler.config_file = os.path.abspath(config_file)  # Store the config file path
    ConfigHandler.image_output_path = os.path.abspath(image_output_path)  # Store the image path
    ConfigHandler.video_download_path = os.path.abspath(video_download_path)  # Store the video path
    ConfigHandler.username = username  # Store the username
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, ConfigHandler)
    print(f"Front End Server running at http://localhost:8000")
    print(f"Using config file: {ConfigHandler.config_file}")
    httpd.serve_forever()

def open_browser():
    webbrowser.open('http://localhost:8000')