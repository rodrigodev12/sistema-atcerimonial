import os
import re
import json
import shared

def limpar_nome_slug(nome: str) -> str:
    import unicodedata
    # Converte para minúsculas e remove "casamento"
    nome = nome.lower().replace("casamento", "")
    # Remove acentos
    nome = "".join(c for c in unicodedata.normalize('NFD', nome) if unicodedata.category(c) != 'Mn')
    # Substitui " e " (com espaços) ou "&" por hifens
    nome = nome.replace("&", "-")
    nome = re.sub(r'\b(e)\b', '-', nome)
    # Substitui qualquer outro caractere não alfanumérico (inclusive espaços) por hifens
    slug = re.sub(r'[^a-z0-9]+', '-', nome).strip('-')
    # Limpa hifens repetidos
    slug = re.sub(r'-+', '-', slug)
    return slug

def gerar():
    print("\n=== GERADOR DE LINKS PERSONALIZADOS (GITHUB PAGES) ===")
    dados = shared.carregar_dados()
    
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)
    
    # Criar index.html principal do docs (redireciona para o app principal)
    with open(os.path.join(docs_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AT Cerimonial</title>
    <meta http-equiv="refresh" content="0; URL='https://sistema-atcerimonial.streamlit.app/'">
</head>
<body>
    <p>Redirecionando para o painel principal...</p>
</body>
</html>""")

    eventos = dados.get("eventos", {})
    if not eventos:
        print("Nenhum evento encontrado para gerar.")
        return
        
    print(f"Encontrados {len(eventos)} eventos. Gerando páginas...")
    
    for ev_id, ev in eventos.items():
        noivos = ev.get("noivos", "Sem Nome")
        token = ev.get("link_token", ev_id)
        
        slug = limpar_nome_slug(noivos)
        if not slug:
            slug = ev_id
            
        slug_dir = os.path.join(docs_dir, slug)
        os.makedirs(slug_dir, exist_ok=True)
        
        # Garante que o título fique bonito (ex: "Casamento Angela e Rodrigo")
        titulo = noivos
        if "casamento" not in titulo.lower():
            titulo = f"Casamento {titulo}"
            
        link_destino = f"https://sistema-atcerimonial.streamlit.app/?ev={token}"
        
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💍 {titulo} — AT Cerimonial</title>
    
    <!-- Metadados de Preview para WhatsApp / Redes Sociais -->
    <meta name="description" content="Acesse o portal exclusivo do seu casamento para acompanhar o checklist de tarefas, fornecedores e cronograma.">
    <meta property="og:title" content="💍 {titulo} — AT Cerimonial">
    <meta property="og:description" content="Acesse o portal exclusivo do seu casamento para acompanhar o checklist de tarefas, fornecedores e cronograma.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://rodrigodev12.github.io/sistema-atcerimonial/{slug}/">
    <meta property="og:image" content="https://raw.githubusercontent.com/rodrigodev12/sistema-atcerimonial/main/docs/preview_logo.png">
    
    <!-- Redirecionamento instantâneo -->
    <meta http-equiv="refresh" content="0; URL='{link_destino}'">
</head>
<body>
    <div style="font-family: sans-serif; text-align: center; margin-top: 100px;">
        <h2>💍 {titulo}</h2>
        <p>Redirecionando para o portal do seu casamento...</p>
        <p style="font-size: 12px; color: #888;">Caso não seja redirecionado automaticamente, <a href="{link_destino}">clique aqui</a>.</p>
    </div>
</body>
</html>"""

        with open(os.path.join(slug_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"  -> Gerado: {noivos} -> /docs/{slug}/index.html")
        print(f"    Link preview: https://rodrigodev12.github.io/sistema-atcerimonial/{slug}/")
        
    print("\n[OK] Concluido! Lembre-se de adicionar, commitar e pushar a pasta 'docs' para o GitHub.")

if __name__ == "__main__":
    gerar()
