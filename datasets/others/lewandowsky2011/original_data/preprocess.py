import argparse
import os
import numpy as np

def format_lewnadoski(df, subj, session, phase, type_, block, choices, block_size=16, organize_by='type', save_dir=None):
    """
    Converts one subject/session/phase/type/block subset of the Lewandowski dataset
    into the model query text format.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset loaded from CSV (lewan11tld.csv).
    subj, session, phase, type_, block : int
        Identifiers for the subset to extract.
    ground_truth : bool
        If True, use ground truth labels for OUT; otherwise, use participant responses.
    block_size : int, optional
        Number of trials in the block (default is 16).
    Returns
    -------
    str
        Formatted text block.
    """

    

    subset = df[(df.subj == subj) & (df.session == session) & 
                (df.phase == phase) & (df.type == type_) & (df.block == block)].copy()
    if subset.empty:
        return f"# No data for subj={subj}, session={session}, phase={phase}, type={type_}, block={block}"

    # Determine dimension order (e.g., ['shape','size','color'])
    dim_order = list(subset[['dim1', 'dim2', 'dim3']].iloc[0])

    # Decode each logstim to human-readable form
    decoded_stims = []
    random_assign = np.random.rand() > 0.5  # Randomize mapping of 0/1 to actual feature values
    for logstim in subset['logstim']:
        stim_bin = str(logstim).zfill(3)
        features = {}
        for dim_name, bit in zip(dim_order, stim_bin):
            # # randomize the mapping of 0/1 to actual feature values
            bit = int(bit) if random_assign else 1 - int(bit)
            if dim_name == 'shape':
                features['shape'] = 'triangle' if int(bit) else 'rectangle'
            elif dim_name == 'color':
                features['color'] = 'yellow' if int(bit) else 'blue'
            elif dim_name == 'size':
                features['size'] = 'size_2' if int(bit) else 'size_1'
        decoded_stims.append(features)

    subset['decoded'] = decoded_stims

    # Format the "IN: ... OUT: ..." lines
    gt_lines = [
            f"IN: {r['decoded']['shape']} {r['decoded']['color']} {r['decoded']['size']} "
            f"OUT: {'yes' if r['logcat'] == 1 else 'no'}" # f"OUT: {'yes' if r['correct'] == 1 else 'no'}"
            for _, r in subset.iterrows()
        ]
    human_lines = [
            f"IN: {r['decoded']['shape']} {r['decoded']['color']} {r['decoded']['size']} "
            f"OUT: {'yes' if r['resp'] == 1 else 'no'}" # f"OUT: {'yes' if r['correct'] == 1 else 'no'}"
            for _, r in subset.iterrows()
        ]

    for query_n in range(1, block_size):  # You can adjust query_n as needed
    
        # Split into SUPPORT and QUERY
        if choices == 'ground_truth' or choices == 'human_only':
            lines = gt_lines if choices == 'ground_truth' else human_lines
            support_lines = lines[:query_n] if len(lines) > query_n else lines
            query_lines = [lines[query_n]] if len(lines) > query_n else []
        elif choices == 'match_humans':
            support_lines = gt_lines[:query_n] if len(gt_lines) > query_n else gt_lines
            query_lines = [human_lines[query_n]] if len(human_lines) > query_n else []


        text = "*SUPPORT*\n" + "\n".join(support_lines)
        if query_lines:
            text += "\n\n*QUERY*\n" + "\n".join(query_lines)
        text += "\n\n*HYPOTHESIS*\nlambda S: lambda x: placeholder(x)\n"

        # # save text to each query_n file
        if organize_by == 'type':
            os.makedirs(f'{save_dir}_{"" if choices == "ground_truth" else "human_" if choices == "human_only" else "match_humans_"}type_level', exist_ok=True)
            os.makedirs(f'{save_dir}_{"" if choices == "ground_truth" else "human_" if choices == "human_only" else "match_humans_"}type_level/type{type_}', exist_ok=True)
            with open(f'{save_dir}_{"" if choices == "ground_truth" else "human_" if choices == "human_only" else "match_humans_"}type_level/type{type_}/lewandowski_subj{subj}_session{session}_phase{phase}_type{type_}_block{block}_query{query_n}.txt', 'w') as f:
                f.write(text)
        elif organize_by == 'flat':
            os.makedirs(f'{save_dir}_{"" if choices == "ground_truth" else "human_" if choices == "human_only" else "match_humans_"}flat', exist_ok=True)
            with open(f'{save_dir}_{"" if choices == "ground_truth" else "human_" if choices == "human_only" else "match_humans_"}flat/lewandowski_subj{subj}_session{session}_phase{phase}_type{type_}_block{block}_query{query_n}.txt', 'w') as f:
                f.write(text)

    return text

if __name__ == "__main__":
    import pandas as pd
    parser = argparse.ArgumentParser()
    parser.add_argument('--choices', type=str, choices=['ground_truth', 'human_only', 'match_humans'], default='ground_truth',
                       help='Which choices to use for OUT labels')
    parser.add_argument('--organize_by', type=str, choices=['type', 'flat'], default='type',
                       help='How to organize output files')
    parser.add_argument('--path_data', type=str, default='~/biml-cogsci/human_data/lewan11tld.csv',
                       help='Path to Lewandowski dataset CSV file')
    parser.add_argument('--save_dir', type=str, default='lewandowski/',
                       help='Directory to save processed text files')
    
    args = parser.parse_args()

    df = pd.read_csv(args.path_data)
    block_size = 16
    # chose 5 random subjects
    # df = df[df['subj'].isin(np.random.choice(df['subj'].unique(), size=5, replace=False))]
    for (subj, session, phase, type_, block) in df[['subj', 'session', 'phase', 'type', 'block']].drop_duplicates().itertuples(index=False):
    # subj, session, phase, type_, block = 2, 1, 1, 3, 1
        text_block = format_lewnadoski(
            df,
            subj=subj,
            session=session,
            phase=phase,
            type_=type_,
            block=block,
            choices=args.choices,
            block_size=block_size,
            organize_by=args.organize_by,
            save_dir=args.save_dir
        )
        print(f"Processed subj={subj}, session={session}, phase={phase}, type={type_}, block={block}")