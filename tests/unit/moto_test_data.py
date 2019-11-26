"""
These functions are written assuming the under a moto call stack.
TODO add check is a fake bucket?
"""
import boto3


def pre_load_s3_data(bucket_name, prefix, region='us-east-1'):
    s3 = boto3.client('s3', region_name=region)
    res = s3.create_bucket(Bucket=bucket_name)

    default_kwargs = {"Body": b"Fake data for testing.", "Bucket": bucket_name}
    s3.put_object(Key=f"{prefix}/readme.txt", **default_kwargs)
    s3.put_object(Key=f"{prefix}/notes.md", **default_kwargs)

    # load items, 3 directories
    for i, _ in enumerate(range(500)):
        res = s3.put_object(Key=f"{prefix}/images/myimage{i}.tif",
                            **default_kwargs)

    for i, _ in enumerate(range(400)):
        s3.put_object(
            Key=f"{prefix}/scripts/myscripts{i}.py",
            **default_kwargs
        )

    for i, _ in enumerate(range(110)):
       s3.put_object(
           Key=f"{prefix}/scripts/subdir/otherscripts{i}.sh",
           **default_kwargs
       )
