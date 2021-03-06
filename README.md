# PuzzleSolver
一款专门为CTF比赛设计的拼图工具

# 前言
因为用PhotoShop等软件无法做到拼图自动对齐，软件最初的设计想法只是做一个工具能方便人工手拼拼图的工具。  

# 如何使用？
最好在Python3.7.8环境下安装，运行main.py即可  
```
pip install -r requirements.txt
python main.py
```
或前往[Release](https://github.com/JamesHoi/PuzzleSolver/releases)下载exe

# 功能
使用教程详见[wiki](https://github.com/JamesHoi/PuzzleSolver/wiki)  
## 基础功能
- [x] 实现拼图碎片块移动及放置
- [x] 添加透明背景图片以方便进行比较 
- [x] 拼图板网格线
- [x] 视窗放大缩小移动、全屏 
- [x] 重置视窗放大比例（有Bug）
- [ ] 保存项目
- [ ] 撤销、复原操作
- [ ] 导出拼接好的图片
- [ ] 导出剩余未拼接的碎片图
- [ ] 可手动将碎片图片分组
- [ ] 重置碎片拼图进度
## 拼图相关
- [x] 用gaps算法自动拼接
- [x] 与原图进行像素点暴力对比，阈值范围内则拼入
- [x] 删除全部除画笔颜色的颜色
- [ ] 自动区分相似碎片图
- [ ] 自动区分含有画笔的碎片图
- [ ] 通过比较碎片图边缘进行自动拼接
## 脚本
- [x] 将多张碎片图拼成一张（需按顺序命名）
- [x] 将一张图片分成多张碎片图
- [x] 将一张图片随机打乱生成一张碎片图
- [ ] 一些图像预处理操作

# 已知问题
- [ ] 重置视角缩放比例，碎片图会消失
- [ ] 将多张碎片图拼成一张时报错
- [ ] 自动拼图后移出第一张拼图会消失
- [ ] 点新增图片并没有删除之前拼好的图片
- [ ] 将自动拼图拼好的移出后点击删除除画笔颜色会错误
- [ ] 自动拼图后缩放比例碎片图会消失
- [ ] 关闭软件弹出提示，点击No或关闭提示窗口还是会关闭，且不会杀死进程
- [ ] 自动拼图时关闭进度窗口并没有杀死进程
- [ ] gaps自动拼图输入参数generations为1时报错
