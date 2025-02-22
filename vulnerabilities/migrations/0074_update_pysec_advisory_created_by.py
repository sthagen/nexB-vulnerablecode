# Generated by Django 4.2.16 on 2024-10-24 13:51

from django.db import migrations

"""
Update the created_by field on Advisory from the old qualified_name
to the new pipeline_id.
"""


def update_created_by(apps, schema_editor):
    from vulnerabilities.pipelines.pysec_importer import PyPIImporterPipeline

    Advisory = apps.get_model("vulnerabilities", "Advisory")
    Advisory.objects.filter(created_by="vulnerabilities.importers.pysec.PyPIImporter").update(
        created_by=PyPIImporterPipeline.pipeline_id
    )


def reverse_update_created_by(apps, schema_editor):
    from vulnerabilities.pipelines.pysec_importer import PyPIImporterPipeline

    Advisory = apps.get_model("vulnerabilities", "Advisory")
    Advisory.objects.filter(created_by=PyPIImporterPipeline.pipeline_id).update(
        created_by="vulnerabilities.importers.pysec.PyPIImporter"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("vulnerabilities", "0073_delete_packagerelatedvulnerability"),
    ]

    operations = [
        migrations.RunPython(update_created_by, reverse_code=reverse_update_created_by),
    ]
