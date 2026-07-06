import json
import os
from supabase import create_client

def migrate():
    db_file = "eventos_db.json"
    if not os.path.exists(db_file):
        print(f"Erro: Arquivo local {db_file} não encontrado.")
        return
        
    print("\n=== AT CERIMONIAL - MIGRAÇÃO DE DADOS PARA SUPABASE ===")
    supabase_url = input("Digite a sua SUPABASE_URL: ").strip()
    supabase_key = input("Digite a sua SUPABASE_KEY (anon/public): ").strip()
    
    if not supabase_url or not supabase_key:
        print("Erro: URL e KEY são obrigatórios.")
        return
        
    try:
        print("\n[1/3] Conectando ao Supabase...")
        supabase = create_client(supabase_url, supabase_key)
        
        print(f"[2/3] Carregando dados locais de {db_file}...")
        with open(db_file, "r", encoding="utf-8") as f:
            dados = json.load(f)
            
        print("[3/3] Sincronizando dados com a nuvem...")
        
        # Tenta atualizar o registro existente
        response = supabase.table("at_cerimonial").select("id").eq("id", "dados_sistema").execute()
        if response.data:
            supabase.table("at_cerimonial").update({"data": dados}).eq("id", "dados_sistema").execute()
            print("\n✅ SUCESSO: Dados atualizados e sobrescritos com sucesso no Supabase!")
        else:
            supabase.table("at_cerimonial").insert({"id": "dados_sistema", "data": dados}).execute()
            print("\n✅ SUCESSO: Dados inseridos pela primeira vez com sucesso no Supabase!")
            
    except Exception as e:
        print(f"\n❌ ERRO: Ocorreu uma falha durante a migração:\n{e}")

if __name__ == "__main__":
    migrate()
