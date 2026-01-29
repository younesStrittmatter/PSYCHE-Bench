import json
from typing import Optional, Any
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).parent.parent


@dataclass
class Validation:
    validation_result: dict
    validation_target: dict

    def to_dict(self):
        return {
            'validation_result': self.validation_result,
            'validation_target': self.validation_target,
        }


@dataclass
class ValidationResult:
    has_validation_run: bool
    valid: Optional[bool] = None
    extracted: Optional[Any] = None
    error_type: Optional[str] = None
    additional_info: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "has_validation_run": self.has_validation_run,
            "extracted": self.extracted,
            "error_type": self.error_type,
            "additional_info": self.additional_info,
        }


@dataclass
class ValidationError:
    error_type: str = 'ValidationError'

    def validation_result(self):
        return ValidationResult(
            has_validation_run=False,
            valid=None,
            extracted=None,
            error_type=self.error_type,
            additional_info=None,
        )

    def to_dict(self) -> dict:
        return self.validation_result().to_dict()


@dataclass
class ColumnsNotFoundError(ValidationError):
    columns: list[str] = None
    error_type: str = 'ColumnNotFound'

    def validation_result(self):
        return ValidationResult(
            has_validation_run=False,
            valid=None,
            error_type=self.error_type,
            additional_info=str(self.columns),
        )


@dataclass
class ValidationNotImplemented(ValidationError):
    validation_implementation: str = None
    error_type: str = 'ValidationNotImplemented'

    def validation_result(self):
        return ValidationResult(
            has_validation_run=False,
            valid=None,
            error_type=self.error_type,
            additional_info=self.validation_implementation,
        )


def run(
        dataset: str = "psych101",
        paper: str = "badham2017deficits",
        method_type: str = "manual",
        method_name: str = "psych101"
):
    target_file_path = _REPO_ROOT / "datasets" / dataset / paper / "targets.json"
    target_data = json.load(open(target_file_path))

    store_path_root = _REPO_ROOT / "evaluation" / method_type / method_name / paper / "evaluation.json"
    store_path_root.parent.mkdir(parents=True, exist_ok=True)
    results = {}
    for experiment_target in target_data['experiments']:
        results[experiment_target['experiment_id']] = evaluate_experiment(experiment_target, method_type, method_name,
                                                                          paper, dataset)

    with open(store_path_root, "w") as store:
        json.dump(results, store)


def evaluate_experiment(experiment_target, method_type, method_name, paper, dataset):
    csv_data_path = _REPO_ROOT / "methods" / method_type / method_name / paper / f"{experiment_target['experiment_id']}.csv"
    csv_data = pd.read_csv(csv_data_path)
    validations = []
    for column, targets in experiment_target['targets'].items():
        for target in targets:
            _validation_res = None
            _type = target["type"]
            value = target.get("value")
            where = target.get("where")
            per = target.get("per")
            if not _type in TYPE_MAP:
                error = ValidationNotImplemented(
                    validation_implementation=str(_type))
                _validation_res = error
            if not _validation_res:
                if column not in csv_data.columns:
                    error = ColumnsNotFoundError(
                        columns=[column],
                    )
                    _validation_res = error
            if not _validation_res:
                res = check_where(where, csv_data)
                if res:
                    _validation_res = res
            if not _validation_res:
                res = check_per(per, csv_data)
                if res:
                    _validation_res = res
            if not _validation_res:
                _validation_res = TYPE_MAP[_type](column, value, where, per, csv_data)
            validations.append(Validation(
                validation_result=_validation_res.to_dict(),
                validation_target=target,
            ))

    data_as_dicts = []
    for validation in validations:
        data_as_dicts.append(validation.to_dict())
    return data_as_dicts


def count_unique(column, target, where, per, data):
    data_to_check = data
    if where:
        for key, value in where.items():
            data_to_check = data_to_check[data_to_check[key] == value]
    if per:
        # normalize to list
        per_cols = [per] if isinstance(per, str) else list(per)

        # find unique group combinations
        groups = data_to_check[per_cols].drop_duplicates()

        correct_results = 0
        extracted = []

        for _, group_vals in groups.iterrows():
            mask = True
            for col in per_cols:
                mask &= data_to_check[col] == group_vals[col]

            _data_to_check_per = data_to_check[mask]
            _unique = _data_to_check_per[column].dropna().unique().tolist()

            extracted.append(len(_unique))
            correct_results += int(len(_unique) == target)

        total = len(groups)

        return ValidationResult(
            has_validation_run=True,
            # now "valid" is proportion correct, just like before
            valid=(correct_results / total) if total else None,
            extracted=extracted,
        )
    unique = data_to_check[column].unique().tolist()
    return ValidationResult(
        has_validation_run=True,
        valid=len(unique) == target,
        extracted=len(unique),
    )


def check_where(where, data):
    if not where:
        return None
    columns_to_check = set(where.keys())
    columns = set(data.columns)

    # columns requested in `where` but missing in dataframe
    missing_columns = columns_to_check - columns

    if missing_columns:
        return ColumnsNotFoundError(
            columns=list(missing_columns),
        )
    return None


def check_per(per, data):
    if not per:
        return None
    columns_to_check = set(per)
    columns = set(data.columns)

    # columns requested in `where` but missing in dataframe
    missing_columns = columns_to_check - columns

    if missing_columns:
        return ColumnsNotFoundError(
            columns=list(missing_columns),
        )
    return None


TYPE_MAP = {
    'count_unique': count_unique,
}

if __name__ == "__main__":
    from itertools import product

    datasets = ["psych101"]
    papers = [
        "badham2017deficits",
        "bahrami2020four",
        "binz2022heuristics"
    ]
    method_types = ["manual"]
    method_names = ["psych101"]
    for dataset, paper, method_type, method_name in product(
            datasets, papers, method_types, method_names
    ):
        run(
            dataset=dataset,
            paper=paper,
            method_type=method_type,
            method_name=method_name,
        )
