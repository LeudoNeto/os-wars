"""
Gerenciador de áudio do jogo
"""

import pygame
import os


class AudioManager:
    """Gerencia músicas de fundo e efeitos sonoros"""
    
    def __init__(self):
        """Inicializa o gerenciador de áudio"""
        pygame.mixer.init()
        
        # Controle de música
        self.current_music = None
        self.paused_music = None  # Música pausada durante combate
        self.music_volume = 0.7
        self.sound_volume = 0.9
        
        # Cache de sons
        self.sounds = {}
    
    def load_sound(self, sound_path):
        """
        Carrega um efeito sonoro
        
        Args:
            sound_path: Caminho para o arquivo de som
            
        Returns:
            pygame.mixer.Sound ou None se falhar
        """
        if sound_path in self.sounds:
            return self.sounds[sound_path]
        
        if not os.path.exists(sound_path):
            print(f"Arquivo de som não encontrado: {sound_path}")
            return None
        
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(self.sound_volume)
            self.sounds[sound_path] = sound
            return sound
        except Exception as e:
            print(f"Erro ao carregar som {sound_path}: {e}")
            return None
    
    def play_sound(self, sound_path):
        """
        Toca um efeito sonoro
        
        Args:
            sound_path: Caminho para o arquivo de som
        """
        sound = self.load_sound(sound_path)
        if sound:
            sound.play()
    
    def play_sound_limited(self, sound_path, max_time_ms=3000):
        """
        Toca um efeito sonoro com duração máxima
        
        Args:
            sound_path: Caminho para o arquivo de som
            max_time_ms: Tempo máximo em milissegundos (padrão: 3000)
        """
        sound = self.load_sound(sound_path)
        if sound:
            sound.play(maxtime=max_time_ms)
    
    def play_music(self, music_path, loops=-1, fade_ms=1000):
        """
        Toca uma música de fundo
        
        Args:
            music_path: Caminho para o arquivo de música
            loops: Número de repetições (-1 para infinito)
            fade_ms: Tempo de fade in em milissegundos
        """
        # Se já está tocando a mesma música, não faz nada
        if self.current_music == music_path and pygame.mixer.music.get_busy():
            return
        
        if not os.path.exists(music_path):
            print(f"Arquivo de música não encontrado: {music_path}")
            return
        
        try:
            # Para a música atual com fade out
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(500)
                pygame.time.wait(500)
            
            # Carrega e toca a nova música
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
            self.current_music = music_path
            
        except Exception as e:
            print(f"Erro ao tocar música {music_path}: {e}")
    
    def stop_music(self, fade_ms=1000):
        """
        Para a música de fundo
        
        Args:
            fade_ms: Tempo de fade out em milissegundos
        """
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)
            self.current_music = None
    
    def set_music_volume(self, volume):
        """
        Define o volume da música
        
        Args:
            volume: Volume de 0.0 a 1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume):
        """
        Define o volume dos efeitos sonoros
        
        Args:
            volume: Volume de 0.0 a 1.0
        """
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
