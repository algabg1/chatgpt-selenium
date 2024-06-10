# @Autor: Felipe Frechiani de Oliveira (https://github.com/felipefo/chat-gpt-api)
# Este programa acessa o site do chatgpt e faz uma pergunta e captura a resposta por meio de um servidor do selenium.
# Somente funcionou usando o firefox com o chrome não funcionou.
# Alterações: Ana Gabriella Gomes 
# Os tempos de espera são grandes, pois é enviado o texto inteiro do documento

from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs

# Função para fazer uma pergunta ao ChatGPT
def ask_gpt(question):

    # Configurações do Selenium para se conectar a um serviço Selenium remoto
    selenium_host = 'localhost'  # Atualize com o endereço IP ou o nome do host do seu serviço Selenium remoto
    selenium_port = '4444'  # Atualize com a porta em que o serviço Selenium remoto está sendo executado
    # URL da página do ChatGPT
    url = "https://chat.openai.com/"
    print("Accessando url do chatgpt:" + url)
    print("Usando o broswer firefox...")
    # Configuração do WebDriver remoto
    webdriver_remote_url = f"http://{selenium_host}:{selenium_port}/wd/hub"
    print("Roda do selenium:" + webdriver_remote_url)
    firefox_options = Options()
    browser = webdriver.Remote(webdriver_remote_url, options=firefox_options)

    # Abre a página do ChatGPT
    try:   
        browser.get(url)
        print("URL da pagina:" + browser.current_url)
        print("Titulo da pagina:" + browser.title)
        time.sleep(5)  # Espera para garantir que a página esteja carregada
        browser.save_screenshot("1_primeira_tela.png")
        print("Primeira tela salva") # Para verificar se inicia no layout esperado
        
        # Insere a pergunta no campo de entrada
        if browser is not None:
            # Após várias solicitações, o ChatGPT começa a pedir que seja feito o login, mas há um botão para continuar sem precisar logar
            # Clica no botão para desconectar
            #disconnect_button = browser.find_element(By.XPATH, '//a[contains(@class, "cursor-pointer") and contains(text(), "Stay logged out")]')
            #disconnect_button.click()
            wait = WebDriverWait(browser, 80)
            browser.save_screenshot("2_tela_antes_da_pergunta.png")
            print("Tela antes da pergunta salva") # Para verificar se a página carregou completamente
            
            # Aguarda até que o elemento esteja presente
            input_field = wait.until(
                EC.element_to_be_clickable((By.ID , "prompt-textarea"))
            )
            actions = ActionChains(browser)
            # Clica no botão
            actions.click(input_field).perform()
            input_field.send_keys(question)
            
            # Aguarda até que o elemento esteja presente
            submit_button = wait.until(
                EC.element_to_be_clickable((By.XPATH , '//button[@data-testid="send-button"]'))
            )
            browser.save_screenshot("3_tela_antes_da_resposta.png")
            print("Tela antes da resposta salva")
            submit_button.click()
            
            # Aguarda a resposta do ChatGPT
            print("aguardando resposta")
            browser.save_screenshot("4_tela_aguardando_resposta.png")
            time.sleep(30)
            browser.save_screenshot("4-1_tela_aguardando_resposta.png")
            response_element = wait.until(
                EC.visibility_of_element_located((By.XPATH, '//div[@data-message-author-role="assistant"]'))
            )
            response = response_element.text
            browser.save_screenshot("5_tela_depois_da_resposta.png")
            print("Tela depois da resposta salva")
            browser.quit()  
            return response
    
    except NoSuchElementException:
        print("Elemento não encontrado na página.")
    except TimeoutException:
        print("Aguardo do elemento excedeu o tempo limite.")
    except WebDriverException as e:
        print(f"Erro no WebDriver: {e}")
    finally:
        if browser:
            browser.quit()  

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_params = parse_qs(post_data.decode('utf-8'))

        if 'question' in post_params:
            question = post_params['question'][0]
            response = ask_gpt(question)  # Suponha que get_gpt_response seja sua função para interagir com o ChatGPT
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'response': response}).encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Bad Request')

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()  

if __name__ == "__main__":
    run()
