# Generated by Django 4.1.13 on 2023-12-05 14:54

from itertools import groupby

from django.db import migrations
from django.db.models import Count

from packageurl import PackageURL

class Migration(migrations.Migration):

    def remove_dupes(apps, _):
        """
        Remove duplicated Package with the same purl and different namespace and name fields.
        Some namespace and name have been stored combined in the name or namespace field
        We are keeping one single normalized variant.
        """
        Package = apps.get_model("vulnerabilities", "Package")

        duplicates = (
            Package.objects
            .values_list("package_url")
            .order_by("package_url")
            .annotate(count_id=Count("id"))
            .filter(count_id__gt=1)
        )

        to_update = []
        to_delete = []
        # Get all rows with the same purl,
        # keep the first to resave and deleted the other ones
        for purl, _cid in duplicates:
            packages = Package.objects.filter(package_url=purl)

            kept_package = packages[0]
            to_update.append(kept_package)

            # discard dupes
            deleted_packages = (p.id for p in packages[1:])
            to_delete.extend(deleted_packages)

        deleted, _ = Package.objects.filter(id__in=to_delete).delete()
        print(f"Deleted {deleted} duplicated Packages")

        # save back with a side effect to normalize package name and namspaces
        for pkg in to_update:
            normalize_and_save_package(pkg)

    dependencies = [
        ("vulnerabilities", "0051_alter_package_unique_together_and_more"),
    ]

    operations = [
        migrations.RunPython(remove_dupes, reverse_code=migrations.RunPython.noop),
    ]


def normalize_and_save_package(package):
    """
    Normalize and save package
    """

    purl = PackageURL(
        type=package.type,
        namespace=package.namespace,
        name=package.name,
    )

    normalized = PackageURL.from_string(str(purl))

    package.namespace = normalized.namespace or ""
    package.name = normalized.name or ""

    package.save()
