FROM flutter:3.19.0-stable

WORKDIR /app

# 复制Flutter项目文件
COPY flutter_remote/pubspec.yaml ./
COPY flutter_remote/lib/ ./lib/

# 获取依赖
RUN flutter pub get

# 构建APK
RUN flutter build apk --release

# 输出结果
RUN ls -la build/app/outputs/flutter-apk/

# 默认命令
CMD ["ls", "-la", "build/app/outputs/flutter-apk/"]
