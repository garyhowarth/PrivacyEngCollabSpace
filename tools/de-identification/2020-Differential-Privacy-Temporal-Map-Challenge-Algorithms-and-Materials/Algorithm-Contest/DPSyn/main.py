import argparse
import numpy as np
import yaml
from loguru import logger

from dataloader.DataLoader import *
from dataloader.RecordPostprocessor import RecordPostprocessor
from method.sample_parallel import Sample
from config.path import *


def main():
    with open(CONFIG_DATA, 'r') as f:
        config = yaml.load(f, Loader=yaml.BaseLoader)

    # dataloader initialization
    dataloader = DataLoader()
    dataloader.load_data()
    parameters = json.loads(Path(config['parameter_spec']).read_text())
    syn_data = None
    for r in parameters["runs"]:
        eps, delta, sensitivity = r['epsilon'], r['delta'], r['max_records_per_individual']
        logger.info(f'working on eps={eps}, delta={delta}, and sensitivity={sensitivity}')
        synthesizer = Sample(dataloader, eps, delta, sensitivity)
        tmp = synthesizer.synthesize()
        tmp['epsilon'] = eps
        if syn_data is None:
            syn_data = tmp
        else:
            syn_data = syn_data.append(tmp, ignore_index=True)

    postprocessor = RecordPostprocessor()
    syn_data = postprocessor.post_process(syn_data, args.config, dataloader.decode_mapping)
    logger.info("post-processed synthetic data")
    syn_data["sim_individual_id"] = 0
    ordered_cols = ["epsilon"] + list(parameters["schema"].keys()) + ["sim_individual_id"]
    syn_data = syn_data[ordered_cols]
    logger.info(f"cols: {syn_data.columns}")
    syn_data.to_csv("submission.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--config", type=str, default="./config/data.yaml",
                        help="specify the path of config file in yaml")
    # parser.add_argument("--method", type=str, default='sample',
    #                     help="specify which method to use")

    args = parser.parse_args()
    main()

