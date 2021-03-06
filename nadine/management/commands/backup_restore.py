import os
import time
import urllib
import datetime
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from nadine.utils.backup import BackupManager


class Command(BaseCommand):
    help = "Deletes and then restores the DB and non-static media from a backup created using the make_backup management command."
    args = "[backup_file_path]"
    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('backup_file', nargs='+', type=str)

    def handle(self, *labels, **options):
        backup_file = options['backup_file'][0]
        manager = BackupManager()
        manager.restore_backup(backup_file)


# Copyright 2017 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
