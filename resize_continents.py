"""
Script para redimensionar permanentemente as imagens dos continentes
"""

import os
from PIL import Image
from game.utils.constants import CONTINENTS_DIR, CONTINENT_FILES

# Fator de escala (40% do tamanho original)
SCALE_FACTOR = 0.4

def resize_continents():
    """Redimensiona todas as imagens dos continentes"""
    print(f"Redimensionando continentes para {int(SCALE_FACTOR * 100)}% do tamanho original...\n")
    
    # Cria backup
    backup_dir = os.path.join(os.path.dirname(CONTINENTS_DIR), "continentes_backup")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Pasta de backup criada: {backup_dir}\n")
    
    for continent, filename in CONTINENT_FILES.items():
        path = os.path.join(CONTINENTS_DIR, filename)
        backup_path = os.path.join(backup_dir, filename)
        
        if not os.path.exists(path):
            print(f"✗ {continent}: arquivo não encontrado")
            continue
        
        try:
            # Abre imagem
            img = Image.open(path)
            original_size = img.size
            
            # Faz backup se ainda não existe
            if not os.path.exists(backup_path):
                img.save(backup_path)
                print(f"  Backup: {filename}")
            
            # Calcula novo tamanho
            new_size = (
                int(original_size[0] * SCALE_FACTOR),
                int(original_size[1] * SCALE_FACTOR)
            )
            
            # Redimensiona com alta qualidade
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Salva sobre o arquivo original
            resized_img.save(path, optimize=True)
            
            print(f"✓ {continent}: {original_size} → {new_size}")
            
        except Exception as e:
            print(f"✗ {continent}: erro - {e}")
    
    print("\n" + "="*60)
    print("✓ Redimensionamento concluído!")
    print(f"  Backups salvos em: {backup_dir}")
    print("="*60)

def restore_backups():
    """Restaura os backups dos continentes"""
    backup_dir = os.path.join(os.path.dirname(CONTINENTS_DIR), "continentes_backup")
    
    if not os.path.exists(backup_dir):
        print("✗ Pasta de backup não encontrada!")
        return
    
    print("Restaurando backups...\n")
    
    for continent, filename in CONTINENT_FILES.items():
        backup_path = os.path.join(backup_dir, filename)
        dest_path = os.path.join(CONTINENTS_DIR, filename)
        
        if not os.path.exists(backup_path):
            print(f"✗ {continent}: backup não encontrado")
            continue
        
        try:
            img = Image.open(backup_path)
            img.save(dest_path)
            print(f"✓ {continent}: restaurado")
        except Exception as e:
            print(f"✗ {continent}: erro - {e}")
    
    print("\n" + "="*60)
    print("✓ Restauração concluída!")
    print("="*60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        restore_backups()
    else:
        print("Este script irá redimensionar as imagens dos continentes.")
        print("Um backup será criado automaticamente.\n")
        response = input("Continuar? (s/n): ")
        
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            resize_continents()
        else:
            print("Operação cancelada.")
