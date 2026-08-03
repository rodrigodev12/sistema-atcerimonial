import sys
from playwright.sync_api import sync_playwright

def main():
    url = "https://sistema-atcerimonial.streamlit.app/"
    print(f"Iniciando verificação do Streamlit em: {url}")
    
    with sync_playwright() as p:
        # Lança o navegador em modo headless
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"Erro ao carregar a página inicial: {e}")
        
        # Aguarda um pequeno momento para renderização do React/Streamlit
        page.wait_for_timeout(5000)
        
        # Tira um screenshot para logs do GitHub Actions
        page.screenshot(path="status_inicial.png")
        print("Screenshot de status inicial salvo como 'status_inicial.png'")
        
        # Procura pelo botão de restauração na página de hibernação
        # O Streamlit costuma usar o texto "Sim, vamos restaurar esse aplicativo!" ou em inglês "Yes, get this app back up!"
        botao_restaurar = page.locator("button:has-text('Sim, vamos restaurar esse aplicativo!'), button:has-text('Yes, get this app back up!')")
        
        if botao_restaurar.count() > 0:
            print("⚠️ Aplicativo em modo de repouso detectado! Clicando no botão para restaurar...")
            botao_restaurar.first.click()
            print("Botão clicado. Aguardando inicialização (limite de 3 minutos)...")
            
            # Aguarda até 3 minutos para o aplicativo acordar (procurando um elemento comum da tela de login, como a palavra "Usuário" ou campo de login)
            try:
                page.wait_for_selector("text=Acesso Restrito, text=Usuário, text=Senha", timeout=180000)
                print("✅ Aplicativo restaurado e ativo com sucesso!")
                page.screenshot(path="status_final.png")
            except Exception as e:
                print("⏳ Tempo esgotado aguardando tela de login, mas a restauração foi iniciada.")
                page.screenshot(path="status_final.png")
        else:
            # Caso não encontre o botão de hibernação, verifica se a tela de login já está visível
            if page.locator("text=Acesso Restrito").count() > 0 or page.locator("text=Usuário").count() > 0:
                print("✅ O aplicativo já está acordado e ativo na tela de login.")
            else:
                print("ℹ️ Aplicativo ativo (ou botão de repouso não detectado). Verifique os screenshots se necessário.")
        
        browser.close()

if __name__ == "__main__":
    main()
