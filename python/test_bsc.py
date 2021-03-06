from gnuradio import gr, digital, blocks, analog
import ldpc
import numpy as np
import random, array, copy

class my_tb(gr.top_block):
    def __init__(self, fname, epsilon, max_iterations):
        gr.top_block.__init__(self)
        self.src = blocks.vector_source_b(())
        print "initializing encoder"
        self.encoder = ldpc.ldpc_encoder_bb(fname)
        print "encoder initialized"
        self.K = self.encoder.get_K()
        self.N = self.encoder.get_N()
        print self.K
        print self.N
        str2Kvec = blocks.stream_to_vector(1, self.K)
        chk2symb = digital.chunks_to_symbols_bf(([1, -1]), 1)
        str2Nvec = blocks.stream_to_vector(4, self.N)
        self.channel = ldpc.bsc_bb(self.N, epsilon)
        self.decoder = ldpc.ldpc_decoder_bb(fname, epsilon, max_iterations)
        print "decoder initialized"
        self.noise = analog.noise_source_f(analog.GR_GAUSSIAN, epsilon, 0)
        self.adder = blocks.add_vff(1)
        Kvec2str = blocks.vector_to_stream(1, self.K)
        Nvec2str = blocks.vector_to_stream(4, self.N)
        self.dst = blocks.vector_sink_b()
        self.connect(self.src, str2Kvec, self.encoder, self.channel,
                self.decoder, Kvec2str, self.dst)

def main():
    fname = "/home/manu/repos/ldpc/gr-ldpc/python/alist-files/96.3.963"
    epsilon = 0.06
    max_iterations = 100
    print "initializing top block"
    tb = my_tb(fname, epsilon, max_iterations)
    K = tb.K
    N = tb.N
    match = 0
    mismatch = 0
    datatpl = array.array('B')
    for i in range(K):
        datatpl.append(0)
    f = open('output', 'w')
    g = open('data', 'w')
    for i in range(100):
        txdata = ()
        for i in range(K):
            X = random.randint(0, 1)
            if X == 1:
                datatpl[i] = 1
                txdata = txdata + (1, )
            else:
                datatpl[i] = 0
                txdata = txdata + (0, )
        g.write("tx data\n")
        g.write(str(datatpl) + "\n")
        tb.src.set_data(datatpl)
        tb.run()
        rx_tpl = tb.dst.data()
        tb.dst.reset()
        g.write("rx data\n")
        g.write(str(rx_tpl) + "\n")
        if np.array_equal(txdata, rx_tpl):
            match += 1
        else:
            mismatch += 1
        _str = str(np.array_equal(txdata, rx_tpl))
        _str = _str + "\t" + str(tb.channel.get_nerr()) + "\t" + str(tb.decoder.get_niterations()) + "\n"
        f.write(_str)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
