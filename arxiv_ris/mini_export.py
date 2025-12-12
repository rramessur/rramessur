import argparse, sys, arxiv

def ris_line(tag, v):
    if not v: return ""
    v = " ".join(str(v).split())
    return f"{tag}  - {v}\n"

def to_ris(r):
    L=[]
    L.append(ris_line("TY","JOUR"))
    L.append(ris_line("TI", r.title))
    for a in r.authors: L.append(ris_line("AU", a.name))
    pub = r.published
    if pub:
        L.append(ris_line("PY", str(pub.year)))
        L.append(ris_line("Y1", pub.strftime("%Y/%m/%d")))
    L.append(ris_line("JO","arXiv")); L.append(ris_line("T2","arXiv"))
    L.append(ris_line("ID", r.entry_id.split("/")[-1])); L.append(ris_line("UR", r.entry_id))
    if getattr(r, "doi", None): L.append(ris_line("DO", r.doi))
    L.append(ris_line("AB", r.summary))
    for c in (r.categories or []): L.append(ris_line("KW", c))
    L.append(ris_line("LA","en")); L.append("ER  - \n")
    return "".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", help="arXiv query string")
    ap.add_argument("--query-file", help="Path to a text file containing the arXiv query")
    ap.add_argument("--max-results", type=int, default=50)
    ap.add_argument("--outfile", default="export.ris")
    ap.add_argument("--page-size", type=int, default=50, help="arXiv client page size (smaller avoids server hiccups)")
    args = ap.parse_args()

    if not args.query and not args.query_file:
        print("Provide --query or --query-file", file=sys.stderr); sys.exit(2)

    q = args.query
    if args.query_file:
        with open(args.query_file, "r", encoding="utf-8") as fh:
            q = fh.read().lstrip("\ufeff").strip()   # strip UTF-8 BOM if present

    client = arxiv.Client(page_size=max(10, min(args.page_size, 200)), delay_seconds=3, num_retries=3)
    search = arxiv.Search(query=q, max_results=args.max_results,
                          sort_by=arxiv.SortCriterion.SubmittedDate,
                          sort_order=arxiv.SortOrder.Descending)

    collected = []
    try:
        for r in client.results(search):
            collected.append(r)
            if len(collected) >= args.max_results:
                break
    except Exception as e:
        # Known issue: UnexpectedEmptyPageError when a page returns empty.
        print(f"Warning: {type(e).__name__}: {e}", file=sys.stderr)

    if not collected:
        print("No results."); return

    with open(args.outfile, "w", encoding="utf-8") as f:
        for r in collected:
            f.write(to_ris(r))
    print(f"Exported {len(collected)} records to {args.outfile}")

if __name__ == "__main__":
    main()
