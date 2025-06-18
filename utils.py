import json

def load_info_commands() -> dict:
    try:
        with open("infos.json", "r", encoding="utf-8") as f:
            info_commands = json.load(f)
        print("[INFO] info_commands.json carregado com sucesso.", info_commands)
        return info_commands
    except Exception as e:
        print(f"[ERRO] Falha ao carregar info_commands: {e}")
        return {}