"""Local host/site workflow. All file paths and exports stay in the project."""
import argparse
import json
from src.structures.hosts import load_cif
from src.structures.service import StructureService


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    host=parser.add_mutually_exclusive_group(required=True)
    host.add_argument('--host',choices=['perovskite','wurtzite','aflow_zns'])
    host.add_argument('--cif',help='Project-local CIF path')
    parser.add_argument('--supercell',nargs=3,type=int,default=[1,1,1],metavar=('A','B','C'))
    parser.add_argument('--target')
    parser.add_argument('--site',type=int,help='Index in expanded cell; omit target/site for site analysis')
    parser.add_argument('--k',type=int,default=3)
    parser.add_argument('--mode',choices=['single_site','symmetry_orbit'],default='single_site')
    parser.add_argument('--export',action='store_true',help='Save unique CIF/JSON bundle inside results/structure_lab/exports')
    args=parser.parse_args(argv)
    if (args.target is None)!=(args.site is None):parser.error('Supply target and site together')
    if args.export and args.site is None:parser.error('--export requires target and site')
    try:
        service=StructureService()
        p={'supercell':args.supercell}
        if args.cif:
            structure,source=load_cif(args.cif)
            from pymatgen.io.cif import CifWriter
            # Preserve original bytes through the service parser, not a rewritten CIF.
            from src.similarity_validation import PROJECT_ROOT
            p['cif_text']=(PROJECT_ROOT/source['path']).read_text(encoding='utf-8-sig')
        else:p['host_id']=args.host
        if args.target is None:
            result=service.analyze(p)
        else:
            p.update(target=args.target,site_index=args.site,k=args.k,mode=args.mode)
            result=service.export(p) if args.export else service.generate(p)
        print(json.dumps(result,indent=2,allow_nan=False))
    except (ValueError,TypeError,OSError) as exc:parser.error(str(exc))


if __name__=='__main__':main()
