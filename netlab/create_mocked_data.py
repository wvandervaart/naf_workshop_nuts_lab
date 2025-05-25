import json
import logging
from pathlib import Path


from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get, napalm_cli

from nornir_rich.progress_bar import RichProgressBar
from nornir_rich.functions import print_result


def collect_napalm_getters(task: Task) -> Result:

    result_getters = task.run(
        napalm_get,
        getters=[
            "get_lldp_neighbors",
            "get_lldp_neighbors_detail",
            "get_interfaces",
            "get_interfaces_counters",
            "get_interfaces_ip",
            "get_bgp_config",
            "get_bgp_neighbors",
            "get_bgp_neighbors_detail",
            "get_facts",
        ],
        severity_level=logging.DEBUG,
    )

    getter_result = result_getters[0]
    if not isinstance(getter_result.result, dict):
        return Result(
            host=task.host, result="napalm_get result is not a dict", failed=True
        )

    device_dir: Path = task.host.get("output_dir") / task.host.name
    device_dir.mkdir(exist_ok=True, parents=True)

    for getter, response in getter_result.result.items():
        output = device_dir / f"{getter}.1"
        with output.open("w") as fp:
            json.dump(response, fp, indent=2)

    result_cmd = task.run(
        napalm_cli,
        commands=[f"show ip route 10.0.0.{x}/32 | json" for x in range(1, 11)],
    )

    for i in range(1, 11):
        with (device_dir / f"cli.1.show_ip_route_10_0_0_{i}_32_json.0").open("w") as fp:
            fp.write(result_cmd[0].result[f"show ip route 10.0.0.{i}/32 | json"])
    
    return Result(host=task.host, result="Successful")


def main(password: str = "admin", output_dir: str = "mocked_napalm_data", verbose: bool = False) -> None:
    nr = InitNornir(config_file="config.yaml")
    nr.inventory.defaults.password = password
    nr.inventory.defaults.data["output_dir"] = Path(output_dir)

    nr_with_processors = nr.with_processors([RichProgressBar()])
    result = nr_with_processors.run(task=collect_napalm_getters)

    print_result(
        result,
        vars=["result", "failed", "diff", "changed"],
        severity_level=logging.DEBUG if verbose else logging.INFO,
    )


if __name__ == "__main__":
    main()
