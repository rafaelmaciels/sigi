#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏛️ SiGI — Utilitário de Backup Automatizado
Gera pacote compactado contendo banco de dados, arquivos de mídia e configurações.

Uso:
  python backup.py
  python backup.py --no-uploads
  python backup.py --keep 10
"""

import os
import sys
import zipfile
import argparse
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent

def executar_backup(no_uploads=False, keep=15, output_dir=None):
    dest_dir = Path(output_dir) if output_dir else (BASE_DIR / "backups")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"backup_sigi_{timestamp}.zip"
    arquivo_zip = dest_dir / nome_arquivo

    print(f"📦 Criando backup do SiGI em: {arquivo_zip.name}...")
    
    total_arquivos = 0
    with zipfile.ZipFile(arquivo_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 1. Banco de Dados SQLite
        db_file = BASE_DIR / "instance" / "sigi.db"
        if db_file.exists():
            zipf.write(db_file, arcname="instance/sigi.db")
            total_arquivos += 1
            print("  [+] Banco de dados SQLite incluído.")
            
        # 2. Arquivo de Configurações (.env)
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            zipf.write(env_file, arcname=".env")
            total_arquivos += 1
            print("  [+] Arquivo de ambiente (.env) incluído.")

        # 3. Uploads de Mídia (Fotos, Documentos, Comprovantes)
        if not no_uploads:
            uploads_dir = BASE_DIR / "app" / "static" / "uploads"
            if uploads_dir.exists():
                count_uploads = 0
                for root, dirs, files in os.walk(uploads_dir):
                    for f in files:
                        if f != ".gitkeep":
                            fpath = Path(root) / f
                            arcname = fpath.relative_to(BASE_DIR)
                            zipf.write(fpath, arcname=str(arcname))
                            count_uploads += 1
                total_arquivos += count_uploads
                print(f"  [+] {count_uploads} arquivos de mídia (uploads) incluídos.")

    tamanho_mb = round(arquivo_zip.stat().st_size / (1024 * 1024), 2)
    print(f"✅ Backup concluído com sucesso! Tamanho total: {tamanho_mb} MB ({total_arquivos} arquivos compactados).")

    # Rotação de backups antigos se keep for definido
    if keep and keep > 0:
        backups_existentes = sorted(list(dest_dir.glob("backup_sigi_*.zip")), key=os.path.getmtime)
        if len(backups_existentes) > keep:
            excesso = len(backups_existentes) - keep
            for i in range(excesso):
                rem = backups_existentes[i]
                rem.unlink()
                print(f"  [-] Rotação: backup antigo removido: {rem.name}")

def main():
    parser = argparse.ArgumentParser(description="Gerador de Backup do SiGI")
    parser.add_argument("--no-uploads", action="store_true", help="Não incluir arquivos de mídia/uploads no backup")
    parser.add_argument("--keep", type=int, default=10, help="Número de backups recentes a manter (padrão: 10)")
    parser.add_argument("--output-dir", type=str, help="Diretório de destino customizado")
    args = parser.parse_args()

    executar_backup(no_uploads=args.no_uploads, keep=args.keep, output_dir=args.output_dir)

if __name__ == "__main__":
    main()
