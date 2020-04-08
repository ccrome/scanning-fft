"""Scanning FFT"""
import numpy as np
from numpy.fft import rfft, rfftfreq
from scipy.signal import get_window

def fft_scanning(fs, data, fft_bins=8192, window='hanning'):
    """Perform a scanning FFT on data.
    parameters:
        fs      :  sample rate
        data    :  1 or 2D data.  If it's 2d, it's [frames, channels]
        fft_bins:  the number of FFT bins.  Must be even
        window  :  any of the scipy windows."""
    if len(data.shape) == 1:
        data = data[:, np.newaxis]
    assert(len(data.shape) == 2)
    # Num fft bins = (n/2)+1.  n = 2*(fft_bins-1)
    blocksize = 2*(fft_bins-1)
    if blocksize > data.shape[0]:
        raise ValueError(f"your computed block size {blocksize} is greater than the length of the input data {data.shape[0]}.  Can't continue")
    segments = data.shape[0]//blocksize
    if data.shape[0] % blocksize:
        data = data[:blocksize*segments, :]
    data = np.array(np.split(data, segments, axis=0))
    # data is now of shape [blocks, blocksize, channels]
    # Now, do an FFT across the blocksize access.  The result should be [blocks, fft_size, channels]
    w = get_window(window, blocksize)
    w = w[np.newaxis, :, np.newaxis]
    data = data * w
    fft_data = rfft(data, axis=1)
    assert(fft_data.shape[0] == data.shape[0])
    assert(fft_data.shape[2] == data.shape[2])
    assert(fft_data.shape[1] == fft_bins)
    # Sum up over the blocks axis
    fft_data = np.abs(fft_data)
    result = np.mean(fft_data, axis=0)
    assert(result.shape[0] == fft_bins)
    assert(result.shape[1] == data.shape[2])
    freqs = rfftfreq(blocksize, d=1.0/fs)
    return freqs, result

if __name__ == '__main__':
    import argparse
    import scipy.io.wavfile as wav
    import matplotlib.pyplot as plt
    def get_args():
        p = argparse.ArgumentParser()
        p.add_argument("input_fn", help="Input filename", nargs='+')
        p.add_argument("-n", "--fft-bins", help="Number of FFT bins, default=2048.  Must be even.", type=int, default=2048)
        p.add_argument("-w", "--window", help="FFT Window.  Default is hanning", default='hanning')
        args = p.parse_args()
        if args.fft_bins % 2 != 0:
            print("Error, number of FFT bins must be even")
        return args
    args = get_args()
    for fn in args.input_fn:
        fs, data = wav.read(fn)
        f, d = fft_scanning(fs, data, fft_bins=args.fft_bins, window=args.window)
        for ch in range(d.shape[1]):
            plt.plot(f, 20*np.log10(d[:, ch]), label=f"{fn}:{ch}")
    plt.grid()
    plt.legend()
    plt.show()
    
