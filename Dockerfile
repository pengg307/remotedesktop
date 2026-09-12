FROM flutter:3.16.0-stable

WORKDIR /app

# 复制项目文件
COPY flutter_remote/pubspec.yaml ./
COPY flutter_remote/lib/ ./lib/

# 获取依赖
RUN flutter pub get

# 构建APK
RUN flutter build apk --release

# 输出构建产物位置
RUN echo "APK built at: /app/build/app/outputs/flutter-apk/app-release.apk"
