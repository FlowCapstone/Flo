from pydub import AudioSegment
from pydub import scipy_effects
from utils.augmentation.song_extensions import song_extensions
from utils.transistion.Transition import Transition

class Loopout(Transition):
    def __init__(self):
        pass


    def loop_out(self, prev_song, next_song, **kwargs):
        """
               :param bar_timestamp: The point at which the bar we want to start transitioning out of
               :param bar_end_timestamp: The end timing time of the specified bar
               :param prev_cutoff: Low-pass freq cutoff for outgoing song
               :param next_cutoff: Low-pass freq cutoff for incoming song during the loop (will be played underneath)
               :param num_full_bars:Number of times to loop the full bar
               :param num_half_bars:Number of times to loop the half-bar
               :param num_quart_bars:Number of times to loop the quarter bar
               :return: returns an AudioSegment with the loop transition in between the two songs.
        """
        bar_time = kwargs.pop('bar_timestamp')
        bar_end_time = kwargs.pop('bar_end_timestamp')
        if kwargs.get('prev_cutoff') is None:
            prev_song_freq_cutoff = kwargs.pop('prev_cutoff')
        else:
            prev_song_freq_cutoff = 4000
        if kwargs.get('next_cutoff') is None:
            next_song_freq_cutoff = kwargs.pop('next_cutoff')
        else:
            next_song_freq_cutoff = 2000
        if kwargs.get('num_full_bars') is None:
            full_repeat = kwargs.pop('num_full_bars')
        else:
            full_repeat = 4
        if kwargs.get('num_half_bars') is None:
            half_repeat = kwargs.pop('num_half_bars')
        else:
            half_repeat = 4
        if kwargs.get('num_quart_bars') is None:
            quarter_repeat = kwargs.pop('num_quart_bars')
        else:
            quarter_repeat = 4
        # Get extension of song file
        next_ext = song_extensions.get(next_song.mime, next_song.mime)
        prev_ext = song_extensions.get(prev_song.mime, prev_song.mime)
        # Create and AudioSegment object from the song_file
        next_song = AudioSegment.from_file(next_song.filename, format=next_ext)
        prev_song = AudioSegment.from_file(prev_song.filename, format=prev_ext)

        prev_song_stripped = prev_song[:bar_time]
        prev_song_bar = prev_song[bar_time:bar_end_time]
        bar_length = bar_end_time - bar_time
        curr_bar_half = prev_song_bar[:bar_length/2]
        curr_bar_quarter = prev_song_bar[:bar_length/4]
        for i in range(full_repeat):
            if i == 0:
                result = prev_song_bar
            else:
                result = result.append(prev_song_bar)
        for i in range(half_repeat):
            result = result.append(curr_bar_half)
        for i in range(quarter_repeat):
            result = result.append(curr_bar_quarter)

        result = scipy_effects.low_pass_filter(result, prev_song_freq_cutoff, order=1)
        overlap_duration = len(result)
        next_song_seg = next_song[:overlap_duration]
        next_song_seg = scipy_effects.low_pass_filter(next_song_seg, next_song_freq_cutoff, order=2)
        result = next_song_seg.overlay(result, gain_during_overlay=-5)

        result = result.append(next_song[overlap_duration:], crossfade=100)
        output = prev_song_stripped.append(result, crossfade=500)
        return output

