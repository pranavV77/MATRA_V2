"""Acquire the explicitly approved official small checkpoint, with no overwrites."""
from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timezone
import hashlib,json,uuid
ROOT=Path(__file__).resolve().parents[2]
URL='https://huggingface.co/mace-foundations/mace-mp-0/resolve/e291ace2bfae073c3ebc7ae2f9479a525989baa7/mace-mp-0b2-small.model'
EXPECTED_SHA256='d5773bf9440e96d6eb8c598f84bd0e6369fcfa432f626a87f890e07da3c651c9'
EXPECTED_BYTES=67622684


def main():
    folder=ROOT/'models/stage_06';path=folder/'mace_mp_0_small.model'
    folder.mkdir(parents=True,exist_ok=True)
    manifest=folder/'checkpoint.json'
    if manifest.exists():
        existing=json.loads(manifest.read_text(encoding='utf-8'))
        if existing.get('sha256')!=EXPECTED_SHA256 or existing.get('bytes')!=EXPECTED_BYTES:
            raise ValueError('Existing manifest differs from frozen official model; it was preserved')
    if path.exists():
        if path.stat().st_size!=EXPECTED_BYTES or hashlib.sha256(path.read_bytes()).hexdigest()!=EXPECTED_SHA256:
            raise ValueError('Existing checkpoint is different or corrupted; it was preserved')
        if not manifest.exists():raise ValueError('Checkpoint exists without its provenance manifest; inspect before continuing')
        print('Official checkpoint already present; size and checksum verified. No files changed.')
        return
    partial=folder/('download_'+uuid.uuid4().hex+'.part')
    digest=hashlib.sha256();size=0
    with urlopen(Request(URL,headers={'User-Agent':'MATRA-local-academic-research'}),timeout=45) as response:
        ctype=response.headers.get('Content-Type','')
        if 'text/html' in ctype:raise ValueError('Checkpoint URL returned HTML')
        with partial.open('xb') as out:
            while block:=response.read(1024*1024):
                size+=len(block)
                if size>300_000_000:raise ValueError('Checkpoint exceeds approved small-model download cap')
                digest.update(block);out.write(block)
    if size!=EXPECTED_BYTES or digest.hexdigest()!=EXPECTED_SHA256:
        raise ValueError('Checkpoint differs from official frozen Hugging Face LFS metadata; partial file retained')
    partial.rename(path)  # Windows rename does not overwrite an existing destination.
    metadata={'model_id':'MACE-MP-0b2-small','path':path.relative_to(ROOT).as_posix(),
              'source_url':URL,'source_code_mapping':'https://github.com/ACEsuit/mace/blob/v0.3.14/mace/calculators/foundations_models.py',
              'retrieved_utc':datetime.now(timezone.utc).isoformat(),'bytes':size,'sha256':digest.hexdigest(),
              'license':'MIT as documented for this MACE-MP checkpoint family',
              'energy_reference':'MPTrj DFT PBE+U training convention; no database correction mixing approved',
              'integrity_note':'Size and SHA-256 verified against official Hugging Face LFS metadata at frozen revision e291ace2bfae073c3ebc7ae2f9479a525989baa7.',
              'selection_note':'Original 0a small GitHub release routes reset connections. Official available 0b2 small selected within approved MACE-MP small-model family; no accuracy advantage claimed.',
              'scientific_accuracy_validated_locally':False}
    target=folder/('restoration_'+uuid.uuid4().hex+'.json') if manifest.exists() else manifest
    with target.open('x',encoding='utf-8') as out:json.dump(metadata,out,indent=2)
    print(json.dumps(metadata,indent=2))


if __name__=='__main__':main()
