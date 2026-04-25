import uuid

from django.db import migrations, models
import django.db.models.deletion
from pgvector.django import VectorField


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("documents", "0001_initial"),
        ("orgs", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS vector;"),
        migrations.CreateModel(
            name="DocumentChunk",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("chunk_index", models.PositiveIntegerField()),
                ("content", models.TextField()),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("embedding", VectorField(dimensions=1536)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "document",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chunks", to="documents.document"),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="document_chunks",
                        to="orgs.organization",
                    ),
                ),
            ],
            options={
                "unique_together": {("document", "chunk_index")},
            },
        ),
        migrations.AddIndex(
            model_name="documentchunk",
            index=models.Index(fields=["organization", "document"], name="rag_docchunk_org_doc_idx"),
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS rag_docchunk_embedding_ivfflat "
                "ON rag_documentchunk USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);"
            ),
            reverse_sql="DROP INDEX IF EXISTS rag_docchunk_embedding_ivfflat;",
        ),
    ]

