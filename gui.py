import tkinter as tk
from tkinter import ttk, scrolledtext
from dotenv import load_dotenv
import os
import google.generativeai as genai
import threading
import time

class GeminiArayuz:
    def __init__(self, root):
        self.root = root
        load_dotenv()
        model_name = os.getenv('GEMINI_MODEL')
        if not model_name:
            raise Exception("HATA: GEMINI_MODEL bulunamadı! Lütfen .env dosyanızı kontrol edin.")
        
        self.root.title(f"Gemini AI ({model_name})")
        self.root.geometry("800x600")

        # API Yapılandırması
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("HATA: GEMINI_API_KEY bulunamadı! Lütfen .env dosyanızı kontrol edin.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat = self.model.start_chat(history=[])

        # Arayüz Bileşenleri
        self.create_widgets()
        
        # Yazma durumu için flag
        self.is_typing = False

    def create_widgets(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Sohbet geçmişi - weight parametresi ile genişleyebilir yapıyoruz
        self.chat_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20)
        self.chat_area.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_area.config(state='disabled')
        
        # Markdown için tag'leri tanımla
        self.chat_area.tag_configure("heading1", font=("TkDefaultFont", 18, "bold"))
        self.chat_area.tag_configure("heading2", font=("TkDefaultFont", 16, "bold"))
        self.chat_area.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))

        # Durum etiketi
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5,0))

        # Mesaj girişi
        self.message_entry = ttk.Entry(main_frame, width=70)
        self.message_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        self.message_entry.bind('<Return>', lambda e: self.send_message())

        # Gönder butonu
        self.send_button = ttk.Button(main_frame, text=">", command=self.send_message)
        self.send_button.grid(row=2, column=1, padx=5, pady=10)

        # Grid yapılandırması - tüm yönlerde genişleyebilmesi için weight'leri ayarlıyoruz
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)  # Sohbet alanının genişleyebilmesi için

    def append_to_chat(self, message, is_user=True, new_response=False):
        self.chat_area.config(state='normal')
        
        if new_response:
            self.chat_area.insert(tk.END, f"\nGemini: ")
        else:
            if is_user:
                self.chat_area.insert(tk.END, f"\nSiz: {message}\n")
            else:
                # Markdown formatını işle
                if message.startswith('# '):
                    self.chat_area.insert(tk.END, message[2:], "heading1")
                elif message.startswith('## '):
                    self.chat_area.insert(tk.END, message[3:], "heading2")
                elif '**' in message:
                    # Bold text işleme
                    parts = message.split('**')
                    for i, part in enumerate(parts):
                        if i % 2 == 1:  # Bold kısımlar
                            self.chat_area.insert(tk.END, part, "bold")
                        else:  # Normal text
                            self.chat_area.insert(tk.END, part)
                else:
                    self.chat_area.insert(tk.END, message)
        
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

    def toggle_input_state(self, state):
        if state:
            self.message_entry.config(state='normal')
            self.send_button.config(state='normal')
            self.status_label.config(text="")
        else:
            self.message_entry.config(state='disabled')
            self.send_button.config(state='disabled')
            self.status_label.config(text="Gemini yanıt yazıyor...")

    def process_message(self, message):
        try:
            self.cancel_response = False
            response = self.chat.send_message(message, stream=True)
            self.root.after(0, lambda: self.append_to_chat("", is_user=False, new_response=True))
            
            buffer = ""
            for chunk in response:
                if self.cancel_response:
                    self.root.after(0, lambda: self.append_to_chat("\n[Yanıt iptal edildi]\n", is_user=False))
                    break
                    
                if chunk.text:
                    text = chunk.text
                    buffer += text
                    
                    # Markdown işaretlerini kontrol et
                    if ('**' in buffer and buffer.count('**') % 2 == 0) or \
                       buffer.endswith(('.', '!', '?', '\n')):
                        self.root.after(0, lambda b=buffer: self.append_to_chat(b, is_user=False))
                        buffer = ""
                        time.sleep(0.1)
            
            if buffer:  # Kalan metni gönder
                self.root.after(0, lambda: self.append_to_chat(buffer, is_user=False))
            
        except Exception as e:
            self.root.after(0, lambda: self.append_to_chat(f"Hata oluştu: {str(e)}", is_user=False))
        finally:
            self.root.after(0, lambda: self.toggle_input_state(True))
            self.is_typing = False

    def send_message(self):
        if self.is_typing:
            return

        message = self.message_entry.get().strip()
        if not message:
            return

        # Kullanıcı mesajını göster
        self.append_to_chat(message, is_user=True)
        self.message_entry.delete(0, tk.END)
        
        # Giriş alanlarını devre dışı bırak
        self.is_typing = True
        self.toggle_input_state(False)

        # Mesaj işlemeyi ayrı bir thread'de başlat
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()

def main():
    root = tk.Tk()
    app = GeminiArayuz(root)
    root.mainloop()

if __name__ == "__main__":
    main() 