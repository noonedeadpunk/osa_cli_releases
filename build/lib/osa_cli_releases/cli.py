import argparse
import osa_cli_releases.releasing as releasing


def analyse_global_requirement_pins(args):
    """Check a package list file for updates on PyPI or on upper constraints"""

    with open(args.file, "r") as global_req_file:
        pins = {
            pin.name: pin.specs
            for pin in releasing.parse_requirements(global_req_file.read())
        }

    latest_versions = releasing.get_pypi_versions(pins.keys())

    if not args.requirements_sha:
        sha = releasing.discover_requirements_sha()
    else:
        sha = args.requirements_sha

    constraints_versions = {
        pin.name: pin.specs for pin in releasing.parse_upper_constraints(sha)
    }
    releasing.print_requirements_state(pins, latest_versions, constraints_versions)


def bump_upstream_repos_shas(args):
    """ Bump upstream projects SHAs.
    :param path: String containing the path of the YAML files formatted for updates
    """

    releasing.bump_upstream_repos_shas(args.path)


def bump_acr(args):
    """ Bump collection versions.
    """

    releasing.update_ansible_collection_requirements(filename=args.file)


def bump_arr(args):
    """ Bump roles SHA and copies releases notes from the openstack roles.
    Also bumps roles from external sources when the branch to bump is master.
    """

    releasing.update_ansible_role_requirements_file(filename=args.file)


def freeze_arr(args):
    """ Freeze all roles shas for milestone releases.
    Bump roles SHA and copies releases notes from the openstack roles.
    Also freezes roles from external sources.
    """

    releasing.freeze_ansible_role_requirements_file(filename=args.file)

def unfreeze_arr(args):
    """ Unfreeze all roles shas for milestone releases.
    Also unfreezes roles from external sources.
    """

    releasing.unfreeze_ansible_role_requirements_file(filename=args.file)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Tooling for releasing OpenStack-Ansible"
    )
    subparsers = parser.add_subparsers(help='subcommand help')

    # check_pins
    check_pins_parser = subparsers.add_parser(
        'check_pins',
        help='Sha used for fetching the upper constraints file in requirements'
    )
    check_pins_parser.add_argument(
        "--requirements_sha",
        help="Sha used for fetching the upper constraints file in requirements",
    )
    check_pins_parser.add_argument(
        "--file",
        help="path to global requirements pin file",
        default="global-requirement-pins.txt",
    )
    check_pins_parser.set_defaults(func=analyse_global_requirement_pins)

    # bump_upstream_shas
    bump_upstream_shas_parser = subparsers.add_parser(
        'bump_upstream_shas',
        help='Bump SHAs of OpenStack services'
    )

    bump_upstream_shas_parser.add_argument(
        "--path",
        action='append',
        help="glob expressions for finding files that contain SHAs",
        default=["playbooks/defaults/repo_packages/*.yml",
                 "inventory/group_vars/*all/*_git.yml"],
    )
    bump_upstream_shas_parser.set_defaults(func=bump_upstream_repos_shas)

    # bump_collections
    bump_collections_parser = subparsers.add_parser(
        'bump_collections',
        help='Bump version of Ansible collections'
    )
    bump_collections_parser.add_argument(
        "--file",
        help="path to ansible-collection-requirements.yml file",
        default="ansible-collection-requirements.yml",
    )
    bump_collections_parser.set_defaults(func=bump_acr)

    # bump_roles
    bump_roles_parser = subparsers.add_parser(
        'bump_roles',
        help='Bump roles SHA and copies releases notes from the openstack roles.'
    )
    bump_roles_parser.add_argument(
        "--file",
        help="path to ansible-role-requirements.yml file",
        default="ansible-role-requirements.yml",
    )
    bump_roles_parser.set_defaults(func=bump_arr)

    # freeze_roles_for_milestone
    freeze_roles_parser = subparsers.add_parser(
        'freeze_roles_for_milestone',
        help='Freeze all roles shas for milestone releases and copy release notes'
    )
    freeze_roles_parser.add_argument(
        "--file",
        help="path to ansible-role-requirements.yml file",
        default="ansible-role-requirements.yml",
    )
    freeze_roles_parser.set_defaults(func=freeze_arr)

    # unfreeze_roles_from_milestone
    unfreeze_roles_parser = subparsers.add_parser(
        'unfreeze_roles_from_milestone',
        help=' Unfreeze all roles shas after milestone release'
    )
    unfreeze_roles_parser.add_argument(
        "--file",
        help="path to ansible-role-requirements.yml file",
        default="ansible-role-requirements.yml",
    )
    freeze_roles_parser.set_defaults(func=unfreeze_arr)

    return parser.parse_args()

def main():
    args = parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
