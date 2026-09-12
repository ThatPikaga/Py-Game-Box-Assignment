# Keeps track of what's currently playing so we don't restart the same track

import pygame

class MusicManager:
    """Simple music manager. Call play(track_key) with a key from assets["music_tracks"]."""

    def __init__(self, music_tracks):
        self.tracks = music_tracks      # {name: filepath}
        self.current_track = None
        self.volume = 0.5
        self.enabled = True

    def play(self, track_key, loop=-1, fade_ms=500):
        """
        Start playing a track. If it's already playing, do nothing.
        track_key: key into self.tracks (e.g. "main_theme", "breakout")
        loop: -1 = infinite, 0 = once
        fade_ms: crossfade duration in ms
        """
        if not self.enabled:
            return

        if track_key == self.current_track and pygame.mixer.music.get_busy():
            return  # already playing

        path = self.tracks.get(track_key)
        if not path:
            print(f"  [MusicManager] No track registered for '{track_key}'")
            return

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(loops=loop, fade_ms=fade_ms)
            self.current_track = track_key
            print(f"  [MusicManager] Now playing: {track_key}")
        except Exception as e:
            print(f"  [MusicManager] Failed to play {track_key}: {e}")

    def stop(self, fade_ms=300):
        # Stop current music with fade-out.
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)
        self.current_track = None

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        pygame.mixer.music.set_volume(self.volume)

    def toggle(self):
        # Toggle music on/off.
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop(200)
        return self.enabled
