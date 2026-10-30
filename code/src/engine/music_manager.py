# Keeps track of the current music and applies the volume from Settings.

import pygame


class MusicManager:
    """Plays launcher music and music found in each game's own folder."""

    def __init__(self, music_tracks):
        self.tracks = music_tracks
        self.current_track = None
        self.volume = 0.5
        self.enabled = True

    def play(self, track_key, loop=-1, fade_ms=500):
        """Play a track by its registered key, even if it is currently muted."""
        path = self.tracks.get(track_key)
        if not path:
            print(f"[MusicManager] No music file found for '{track_key}'")
            return

        try:
            if track_key == self.current_track and pygame.mixer.music.get_busy():
                return
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.volume if self.enabled else 0)
            pygame.mixer.music.play(loops=loop, fade_ms=fade_ms)
            self.current_track = track_key
            print(f"[MusicManager] Now playing: {track_key}")
        except Exception as error:
            print(f"[MusicManager] Could not play {track_key}: {error}")

    def stop(self, fade_ms=300):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)
        self.current_track = None

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume if self.enabled else 0)

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)
        pygame.mixer.music.set_volume(self.volume if self.enabled else 0)

    def toggle(self):
        self.set_enabled(not self.enabled)
        return self.enabled
