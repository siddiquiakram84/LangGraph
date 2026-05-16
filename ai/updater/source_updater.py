"""
updater/source_updater.py

Safe AST-based locator updater with backup support.
"""

import ast
import astor
import shutil
import os
import time


class SourceUpdater:

    def update(self, file_path, old_locator, new_locator):

        if not os.path.exists(file_path):
            return False

        # Backup original file
        backup_path = f"{file_path}.bak_{int(time.time())}"

        shutil.copy(file_path, backup_path)

        with open(file_path, "r") as f:

            tree = ast.parse(f.read())

        updated = False

        class LocatorTransformer(ast.NodeTransformer):

            def visit_Constant(self, node):

                nonlocal updated

                if node.value == old_locator[1]:

                    updated = True

                    return ast.Constant(value=new_locator[1])

                return node

        transformer = LocatorTransformer()

        new_tree = transformer.visit(tree)

        if updated:

            with open(file_path, "w") as f:

                f.write(astor.to_source(new_tree))

            return True

        return False
