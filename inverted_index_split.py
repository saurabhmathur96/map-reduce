import argparse
from os import makedirs, path, listdir

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("n_lines", type=int)
    parser.add_argument("indir", type=str)
    parser.add_argument("outdir", type=str)
    args = parser.parse_args()

    makedirs(args.outdir, exist_ok=True)
    for filename in listdir(args.indir):
        infile = path.join(args.indir, filename)
        with open(infile, "rb") as handle:
            buffer = []
            i = 1
            for line in handle:
                
                # Encoding to ASCII because Unicode character handling is messy
                line = line.decode("ascii", "ignore").strip()
                if len(line) == 0:
                    continue
                buffer.append(line)

                if len(buffer) == args.n_lines:
                    
                    outpath = path.join(args.outdir, "%s-%s" % (filename, i))
                    buffer = [filename] + buffer # add document id as first line
                    open(outpath, "w").write("\n".join(buffer))
                    
                    i += 1
                    buffer = [] 
            
            if len(buffer) > 0:
                outpath = path.join(args.outdir, "%s-%s" % (filename, i))
                buffer = [filename] + buffer # add document id as first line
                open(outpath, "w").write("\n".join(buffer))

