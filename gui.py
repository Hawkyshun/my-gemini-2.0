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
        self.root.title("Gemini AI Sohbet Arayüzü")
        self.root.geometry("800x600")

        # API Yapılandırması
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("HATA: GEMINI_API_KEY bulunamadı! Lütfen .env dosyanızı kontrol edin.")
        
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-thinking-exp-1219')  # Varsayılan olarak gemini 2.0 flash thinking exp 1219 kullan
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
            
            accumulated_text = ""
            for chunk in response:
                if self.cancel_response:
                    self.root.after(0, lambda: self.append_to_chat("\n[Yanıt iptal edildi]\n", is_user=False))
                    break
                    
                if chunk.text:
                    accumulated_text += chunk.text
                    words = accumulated_text.split()
                    
                    while len(words) > 0 and not self.cancel_response:
                        # Her seferinde 6 kelime al
                        display_words = " ".join(words[:6]) + " "
                        words = words[6:]
                        self.root.after(0, lambda w=display_words: self.append_to_chat(w, is_user=False))
                        accumulated_text = " ".join(words)
                        time.sleep(0.05)  # Hala küçük bir gecikme bırakıyoruz
            
            if not self.cancel_response:
                self.root.after(0, lambda: self.append_to_chat("\n", is_user=False))
            
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