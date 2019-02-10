import argparse
from os import makedirs, path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("n_lines", type=int)
    parser.add_argument("infile", type=str)
    parser.add_argument("outdir", type=str)
    args = parser.parse_args()

    makedirs(args.outdir, exist_ok=True)
    with open(args.infile, "rb") as handle:
        buffer = []
        i = 1
        for line in handle:
            
            # Encoding to ASCII because Unicode character handling is messy
            line = line.decode("ascii", "ignore").strip()
            if len(line) == 0:
                continue
            buffer.append(line)

            if len(buffer) == args.n_lines:
                outpath = path.join(args.outdir, "%s-%s" % (args.infile, i))
                open(outpath, "w").write("\n".join(buffer))
                
                i += 1
                buffer = [] 
        
        if len(buffer) > 0:
            outpath = path.join(args.outdir, "%s-%s" % (args.infile, i))
            open(outpath, "w").write("\n".join(buffer))

