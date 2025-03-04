#!/bin/bash

# 从version.py获取版本号
VERSION=$(python3 -c "from app.core.version import get_version; print(get_version())")
if [ $? -ne 0 ]; then
    echo "错误: 无法获取版本号"
    exit 1
fi
IMAGE_NAME="config-center"
REGISTRY=""
LATEST=false

# 显示帮助信息
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help          显示帮助信息"
    echo "  -n, --name          设置镜像名称 (默认: config-center)"
    echo "  -r, --registry      设置镜像仓库地址"
    echo "  -v, --version       设置版本号 (默认: 1.0.0)"
    echo "  -l, --latest        同时构建latest标签"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            show_help
            exit 0
            ;;
        -n|--name)
            IMAGE_NAME="$2"
            shift
            shift
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift
            shift
            ;;
        -v|--version)
            VERSION="$2"
            shift
            shift
            ;;
        -l|--latest)
            LATEST=true
            shift
            ;;
        *)
            echo "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 构建完整的镜像名称
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE_NAME="$REGISTRY/$IMAGE_NAME"
else
    FULL_IMAGE_NAME="$IMAGE_NAME"
fi

# 构建Docker镜像
echo "开始构建Docker镜像: $FULL_IMAGE_NAME:$VERSION"
if ! docker build -t "$FULL_IMAGE_NAME:$VERSION" .; then
    echo "错误: Docker镜像构建失败"
    exit 1
fi

# 如果指定了latest标签，则也构建latest版本
if [ "$LATEST" = true ]; then
    echo "标记latest版本"
    if ! docker tag "$FULL_IMAGE_NAME:$VERSION" "$FULL_IMAGE_NAME:latest"; then
        echo "错误: 标记latest版本失败"
        exit 1
    fi

    # 如果设置了镜像仓库，推送latest版本
    if [ -n "$REGISTRY" ]; then
        echo "推送latest版本到镜像仓库"
        if ! docker push "$FULL_IMAGE_NAME:latest"; then
            echo "错误: 推送latest版本失败"
            exit 1
        fi
    fi
fi

# 如果设置了镜像仓库，推送版本化的镜像
if [ -n "$REGISTRY" ]; then
    echo "推送版本化镜像到镜像仓库"
    if ! docker push "$FULL_IMAGE_NAME:$VERSION"; then
        echo "错误: 推送版本化镜像失败"
        exit 1
    fi
fi

echo "构建完成!"
echo "镜像信息:"
echo "  名称: $FULL_IMAGE_NAME"
echo "  版本: $VERSION"
if [ "$LATEST" = true ]; then
    echo "  latest标签: 是"
fi