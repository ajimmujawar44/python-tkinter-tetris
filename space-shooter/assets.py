"""
Space Shooter - Asset Manager & Generator
Handles loading and procedural generation of high-quality visual sprites and retro sound effects.
Ensures the game runs self-contained without missing external assets.
"""

import math
import os
import random
import struct
import wave
import pygame
from settings import (
    IMAGES_DIR,
    SOUNDS_DIR,
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_PURPLE,
    COLOR_RED,
    COLOR_WHITE,
    COLOR_YELLOW,
    SFX_VOLUME,
)


class DummySound:
    """Safe fallback sound when audio device or sound file is unavailable."""
    def play(self, *args, **kwargs):
        pass

    def set_volume(self, *args, **kwargs):
        pass


class AssetManager:
    """Central repository for game images, fonts, and sound effects."""

    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.audio_ready = False
        self._init_audio()
        self._ensure_asset_directories()
        self._prepare_images()
        self._prepare_sounds()

    def _init_audio(self):
        """Safely initialize the Pygame mixer."""
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.pre_init(44100, -16, 2, 512)
                pygame.mixer.init()
                self.audio_ready = True
            except Exception as e:
                print(f"[Warning] Audio device initialization failed: {e}. Running in silent mode.")
                self.audio_ready = False
        else:
            self.audio_ready = True

    def _ensure_asset_directories(self):
        """Ensure images and sounds directories exist on disk."""
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Visual Asset Generation & Loading
    # -------------------------------------------------------------------------

    def _prepare_images(self):
        """Load images from disk or generate them if absent."""
        image_creators = {
            "player": self._generate_player_surface,
            "scout": self._generate_scout_surface,
            "interceptor": self._generate_interceptor_surface,
            "cruiser": self._generate_cruiser_surface,
            "bullet_player": self._generate_player_bullet_surface,
            "bullet_enemy": self._generate_enemy_bullet_surface,
            "life_icon": self._generate_life_icon_surface,
            "shield": self._generate_shield_surface,
        }

        for name, generator in image_creators.items():
            path = IMAGES_DIR / f"{name}.png"
            if path.exists():
                try:
                    surface = pygame.image.load(str(path)).convert_alpha()
                    self.images[name] = surface
                except Exception:
                    surface = generator()
                    self._save_surface(surface, path)
                    self.images[name] = surface
            else:
                surface = generator()
                self._save_surface(surface, path)
                self.images[name] = surface

    def _save_surface(self, surface: pygame.Surface, path):
        """Save a generated Pygame surface as a PNG file."""
        try:
            pygame.image.save(surface, str(path))
        except Exception as e:
            print(f"[Notice] Could not cache {path.name}: {e}")

    def _generate_player_surface(self) -> pygame.Surface:
        """Create a sleek player spaceship sprite (delta-wing interceptor)."""
        w, h = 54, 50
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Hull body (aerodynamic delta wings)
        body_pts = [
            (w // 2, 2),            # Nose tip
            (w - 6, h - 14),        # Right wing tip
            (w - 14, h - 6),        # Right engine notch
            (w // 2 + 5, h - 10),   # Right engine base
            (w // 2 - 5, h - 10),   # Left engine base
            (14, h - 6),            # Left engine notch
            (6, h - 14),            # Left wing tip
        ]
        # Main hull gradient/fill
        pygame.draw.polygon(surf, (25, 45, 75), body_pts)
        pygame.draw.polygon(surf, COLOR_CYAN, body_pts, width=2)

        # Inner cockpit canopy
        cockpit_pts = [
            (w // 2, 8),
            (w // 2 + 6, 26),
            (w // 2, 32),
            (w // 2 - 6, 26),
        ]
        pygame.draw.polygon(surf, (180, 240, 255), cockpit_pts)
        pygame.draw.polygon(surf, COLOR_WHITE, cockpit_pts, width=1)

        # Wing cannons
        pygame.draw.rect(surf, (150, 180, 210), (9, h - 22, 3, 10))
        pygame.draw.rect(surf, (150, 180, 210), (w - 12, h - 22, 3, 10))
        pygame.draw.circle(surf, COLOR_CYAN, (10, h - 22), 2)
        pygame.draw.circle(surf, COLOR_CYAN, (w - 11, h - 22), 2)

        # Twin engine exhausts (glow placeholder)
        pygame.draw.rect(surf, (0, 180, 255), (w // 2 - 10, h - 9, 6, 4))
        pygame.draw.rect(surf, (0, 180, 255), (w // 2 + 4, h - 9, 6, 4))

        return surf

    def _generate_scout_surface(self) -> pygame.Surface:
        """Create a red/crimson agile scout raider sprite."""
        w, h = 42, 38
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        pts = [
            (w // 2, h - 4),     # Bottom beak
            (w - 4, 8),          # Top right wing
            (w - 12, 16),        # Right inner notch
            (w // 2 + 4, 4),     # Engine right
            (w // 2 - 4, 4),     # Engine left
            (12, 16),            # Left inner notch
            (4, 8),              # Top left wing
        ]
        pygame.draw.polygon(surf, (70, 15, 25), pts)
        pygame.draw.polygon(surf, COLOR_RED, pts, width=2)

        # Eye / Sensor core
        pygame.draw.circle(surf, COLOR_ORANGE, (w // 2, h // 2), 5)
        pygame.draw.circle(surf, COLOR_YELLOW, (w // 2, h // 2), 2)
        return surf

    def _generate_interceptor_surface(self) -> pygame.Surface:
        """Create a nimble purple chevron-wing interceptor sprite."""
        w, h = 36, 34
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        pts = [
            (w // 2, h - 2),     # Nose facing down
            (w - 2, 4),          # Right wing spike
            (w // 2, 12),        # Rear center notch
            (2, 4),              # Left wing spike
        ]
        pygame.draw.polygon(surf, (45, 15, 65), pts)
        pygame.draw.polygon(surf, COLOR_PURPLE, pts, width=2)

        # Plasma reactor core
        pygame.draw.circle(surf, (220, 150, 255), (w // 2, 18), 4)
        return surf

    def _generate_cruiser_surface(self) -> pygame.Surface:
        """Create an imposing heavy battlecruiser with plating."""
        w, h = 58, 54
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Main armored chassis
        chassis = [
            (w // 2, h - 2),      # Front ram
            (w - 8, h - 18),     # Forward right armor
            (w - 4, 10),         # Rear right fin
            (w - 18, 4),         # Top right engine
            (18, 4),             # Top left engine
            (4, 10),             # Rear left fin
            (8, h - 18),         # Forward left armor
        ]
        pygame.draw.polygon(surf, (55, 30, 15), chassis)
        pygame.draw.polygon(surf, COLOR_ORANGE, chassis, width=2)

        # Heavy armor plates
        pygame.draw.rect(surf, (110, 60, 25), (w // 2 - 10, 12, 20, 16))
        pygame.draw.rect(surf, COLOR_YELLOW, (w // 2 - 10, 12, 20, 16), width=1)

        # Double heavy cannons
        pygame.draw.line(surf, COLOR_ORANGE, (14, 20), (14, h - 10), 3)
        pygame.draw.line(surf, COLOR_ORANGE, (w - 14, 20), (w - 14, h - 10), 3)
        return surf

    def _generate_player_bullet_surface(self) -> pygame.Surface:
        """Create a glowing cyan laser bolt with luminous aura."""
        w, h = 8, 20
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Outer glow
        pygame.draw.ellipse(surf, (0, 180, 255, 120), (0, 0, w, h))
        # Inner core
        pygame.draw.ellipse(surf, COLOR_WHITE, (2, 2, w - 4, h - 4))
        return surf

    def _generate_enemy_bullet_surface(self) -> pygame.Surface:
        """Create an enemy crimson energy pulse."""
        w, h = 8, 14
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (255, 60, 60, 140), (0, 0, w, h))
        pygame.draw.ellipse(surf, COLOR_YELLOW, (2, 2, w - 4, h - 4))
        return surf

    def _generate_life_icon_surface(self) -> pygame.Surface:
        """Miniature player ship icon for lives indicator."""
        w, h = 20, 18
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pts = [(w // 2, 1), (w - 2, h - 2), (w // 2, h - 6), (2, h - 2)]
        pygame.draw.polygon(surf, COLOR_CYAN, pts)
        return surf

    def _generate_shield_surface(self) -> pygame.Surface:
        """Semi-transparent glowing energy shield dome."""
        radius = 34
        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 240, 255, 70), (radius, radius), radius)
        pygame.draw.circle(surf, (180, 250, 255, 200), (radius, radius), radius, width=2)
        return surf

    # -------------------------------------------------------------------------
    # Audio Synthesis & Loading
    # -------------------------------------------------------------------------

    def _prepare_sounds(self):
        """Generate and load sound effects safely."""
        sound_generators = {
            "laser": self._synthesize_laser_wav,
            "explosion": self._synthesize_explosion_wav,
            "hit": self._synthesize_hit_wav,
            "game_over": self._synthesize_game_over_wav,
            "start": self._synthesize_start_wav,
        }

        for name, generator in sound_generators.items():
            wav_path = SOUNDS_DIR / f"{name}.wav"
            if not wav_path.exists():
                try:
                    generator(wav_path)
                except Exception as e:
                    print(f"[Notice] Could not synthesize {name}.wav: {e}")

            if self.audio_ready and wav_path.exists():
                try:
                    snd = pygame.mixer.Sound(str(wav_path))
                    snd.set_volume(SFX_VOLUME)
                    self.sounds[name] = snd
                except Exception as e:
                    print(f"[Warning] Failed loading sound {name}: {e}")
                    self.sounds[name] = DummySound()
            else:
                self.sounds[name] = DummySound()

    def _write_pcm_wav(self, file_path, samples, sample_rate=44100):
        """Helper to serialize mono 16-bit PCM samples to a .wav file."""
        with wave.open(str(file_path), "wb") as wav_file:
            wav_file.setnchannels(1)      # Mono
            wav_file.setsampwidth(2)      # 16-bit
            wav_file.setframerate(sample_rate)
            raw_data = bytearray()
            for s in samples:
                # Clamp between -32767 and 32767
                val = max(-32767, min(32767, int(s)))
                raw_data.extend(struct.pack("<h", val))
            wav_file.writeframes(raw_data)

    def _synthesize_laser_wav(self, path):
        """Generate a punchy retro sci-fi laser shot sound."""
        sr = 44100
        duration = 0.18
        num_samples = int(sr * duration)
        samples = []
        phase = 0.0

        for i in range(num_samples):
            t = i / num_samples
            # Frequency sweeps rapidly from 900 Hz down to 180 Hz
            freq = 900 * math.exp(-3.5 * t)
            phase += 2 * math.pi * freq / sr
            # Sharp envelope
            envelope = (1.0 - t) ** 1.8
            # Modulated wave (sine + slight square harmonic)
            sample = (0.75 * math.sin(phase) + 0.25 * (1 if math.sin(phase) > 0 else -1))
            samples.append(sample * envelope * 24000)

        self._write_pcm_wav(path, samples, sr)

    def _synthesize_explosion_wav(self, path):
        """Generate a crunchy bass-heavy rumble explosion."""
        sr = 44100
        duration = 0.55
        num_samples = int(sr * duration)
        samples = []
        low_pass = 0.0

        for i in range(num_samples):
            t = i / num_samples
            envelope = (1.0 - t) ** 2.2
            noise = (random.random() * 2 - 1)
            # Low-pass filter to simulate shockwave boom
            low_pass += (noise - low_pass) * 0.15
            low_rumble = math.sin(2 * math.pi * 65 * (1 - 0.5 * t) * (i / sr))
            sample = (0.65 * low_pass + 0.35 * low_rumble) * envelope
            samples.append(sample * 28000)

        self._write_pcm_wav(path, samples, sr)

    def _synthesize_hit_wav(self, path):
        """Generate a brief metallic impact ping."""
        sr = 44100
        duration = 0.1
        num_samples = int(sr * duration)
        samples = []

        for i in range(num_samples):
            t = i / num_samples
            envelope = math.exp(-22 * t)
            freq = 480 + 120 * math.cos(2 * math.pi * 30 * t)
            sample = math.sin(2 * math.pi * freq * (i / sr))
            samples.append(sample * envelope * 22000)

        self._write_pcm_wav(path, samples, sr)

    def _synthesize_game_over_wav(self, path):
        """Generate a dramatic descending synth sequence."""
        sr = 44100
        duration = 0.9
        num_samples = int(sr * duration)
        samples = []
        notes = [370, 311, 277, 220]  # Descending notes

        for i in range(num_samples):
            t = i / sr
            note_idx = min(int(t / (duration / len(notes))), len(notes) - 1)
            freq = notes[note_idx]
            sub_t = (t % (duration / len(notes))) / (duration / len(notes))
            envelope = (1.0 - sub_t) ** 1.3
            sample = math.sin(2 * math.pi * freq * t) * envelope
            samples.append(sample * 20000)

        self._write_pcm_wav(path, samples, sr)

    def _synthesize_start_wav(self, path):
        """Generate an energetic ascending game-start fanfare."""
        sr = 44100
        duration = 0.5
        num_samples = int(sr * duration)
        samples = []
        notes = [261.6, 329.6, 392.0, 523.2]  # C Major arpeggio

        for i in range(num_samples):
            t = i / sr
            note_idx = min(int(t / (duration / len(notes))), len(notes) - 1)
            freq = notes[note_idx]
            sub_t = (t % (duration / len(notes))) / (duration / len(notes))
            envelope = (1.0 - sub_t) ** 1.1
            sample = math.sin(2 * math.pi * freq * t) * envelope
            samples.append(sample * 20000)

        self._write_pcm_wav(path, samples, sr)

    def play_sound(self, name: str):
        """Safely trigger a sound effect by name."""
        if self.audio_ready and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

    def get_image(self, name: str) -> pygame.Surface:
        """Retrieve an image surface by key."""
        return self.images.get(name)
