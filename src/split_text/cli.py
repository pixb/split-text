"""命令行接口"""

import sys
import click
from pathlib import Path

from .splitter import TextSplitter, split_text


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """split-text: 将长文本按语义拆分为较小片段的工具"""
    pass


@cli.command()
@click.argument("text", required=False)
@click.option(
    "-l", "--max-length",
    type=int,
    default=200,
    help="单个片段的最大字符数 (默认: 200)",
)
@click.option(
    "-m", "--min-chunk-length",
    type=int,
    default=50,
    help="合并短片段的最小长度阈值 (默认: 50)",
)
@click.option(
    "--no-merge",
    is_flag=True,
    help="不合并过短的片段",
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="输出文件路径 (默认: 输出到stdout)",
)
def split(text, max_length, min_chunk_length, no_merge, output):
    """拆分文本为较小的片段
    
    如果未提供TEXT参数，将从stdin读取。
    """
    # 获取文本
    if text is None:
        if sys.stdin.isatty():
            click.echo("请输入要拆分的文本:", err=True)
            sys.exit(1)
        text = sys.stdin.read()
    
    # 拆分文本
    splitter = TextSplitter(
        max_length=max_length,
        min_chunk_length=min_chunk_length,
        merge_short=not no_merge,
    )
    result = splitter.split(text)
    
    # 输出结果
    output_content = "\n".join(result.chunks)
    
    if output:
        Path(output).write_text(output_content, encoding="utf-8")
        click.echo(f"已保存到: {output}")
    else:
        click.echo(output_content)
    
    # 显示统计信息
    click.echo(f"\n统计信息:", err=True)
    click.echo(f"  原始长度: {result.metadata['original_length']} 字符", err=True)
    click.echo(f"  片段数量: {result.metadata['chunk_count']}", err=True)
    click.echo(f"  最大长度: {result.metadata['max_length']}", err=True)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "-l", "--max-length",
    type=int,
    default=200,
    help="单个片段的最大字符数 (默认: 200)",
)
@click.option(
    "-o", "--output-dir",
    type=click.Path(),
    help="输出目录 (默认: 当前目录)",
)
def file(input_file, max_length, output_dir):
    """拆分文件中的文本
    
    读取文件内容，拆分为多个片段，并保存到输出目录。
    """
    # 读取文件
    text = Path(input_file).read_text(encoding="utf-8")
    
    # 拆分文本
    result = split_text(text, max_length=max_length)
    
    # 输出目录
    output_path = Path(output_dir) if output_dir else Path.cwd()
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存每个片段
    input_stem = Path(input_file).stem
    
    for i, chunk in enumerate(result.chunks, 1):
        output_file = output_path / f"{input_stem}_part{i:03d}.txt"
        output_file.write_text(chunk, encoding="utf-8")
        click.echo(f"已保存: {output_file}")
    
    # 统计信息
    click.echo(f"\n完成! 共生成 {result.metadata['chunk_count']} 个文件", err=True)


@cli.command()
@click.argument("text")
@click.option(
    "-l", "--max-length",
    type=int,
    default=200,
    help="单个片段的最大字符数 (默认: 200)",
)
def preview(text, max_length):
    """预览拆分结果
    
    显示文本将被如何拆分，不保存文件。
    """
    result = split_text(text, max_length=max_length)
    
    click.echo(f"原始文本 ({result.metadata['original_length']} 字符):\n", err=True)
    click.echo("-" * 50, err=True)
    click.echo(text)
    click.echo("-" * 50, err=True)
    click.echo(f"\n拆分结果 ({result.metadata['chunk_count']} 个片段):\n", err=True)
    
    for i, chunk in enumerate(result.chunks, 1):
        click.echo(f"[{i:2d}] ({len(chunk):3d}字符) {chunk}")
        if i < len(result.chunks):
            click.echo()


def main():
    cli()


if __name__ == "__main__":
    main()