import subprocess
import os.path


def create_style_xml(carto_sytle_path: str):
    """
    create style.xml through carto project.mml
    :return:
    """
    subprocess.run(
        "carto project.mml > style.xml".format(carto_sytle_path),
        cwd=carto_sytle_path,
        shell=True,
        stderr=subprocess.PIPE,
    )


def get_style_xml(generate_style_xml: bool, carto_sytle_path: str) -> str:
    """

    :param generate_style_xml:
    :return:
    """
    if generate_style_xml:
        return subprocess.run(
            "carto {}/project.mml 1>&2".format(carto_sytle_path),
            cwd=carto_sytle_path,
            shell=True,
            stderr=subprocess.PIPE,
        ).stderr.decode("utf-8")
    else:

        if not os.path.isfile("{}/style.xml".format(carto_sytle_path)):
            # create style.xml if not exists
            create_style_xml(carto_sytle_path=carto_sytle_path)

        return open(
            "{}/style.xml".format(carto_sytle_path), "r", encoding="utf-8"
        ).read()
