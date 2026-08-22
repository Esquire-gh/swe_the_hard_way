# Predict, then check. Each chunk in a chunked response is a length written in
# hexadecimal, then that many bytes. stream.py sends one word at a time with a
# trailing space, so each chunk's length is len(word) + 1, in hex. Work out
# the column of hex lengths yourself before you run this.
sentence = "a model answering is a server writing text down a socket"
for word in sentence.split():
    piece = word + " "
    n = len(piece)
    print("%-12r %2d bytes  ->  %s" % (piece, n, format(n, "x")))
