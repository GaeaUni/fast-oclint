# fast-oclint
在git提交代码的时候快速进行增量oclint
![image](https://user-images.githubusercontent.com/8058245/160628327-2e3320a3-5e7b-43ae-b298-980a23f9d3c1.png)


## demo使用方法
1.拉取本工程

2.git submodule update --recursive --init

3.cd demo/LLVM-Tool-Demo

4.pod install

5.../YTKNetwork

6.在YTKNetwork修改任意m文件，或者h文件代码，然后git commit -a -m "XXX"的时候会自动进行快速的oclint

## 其它工程的使用方法
1.拉取本工程

2.拉取自己的工程

3.在podfile里面加上
post_install do |installer|
  puts `python3 path/to/precommit_installer.py`
end

4.pod install

5.之后在developer pod里面提交代码的时候会自动进行增量oclint检查

执行的时候一定要确保oclint有执行权限且安装了xcode命令行，fast-oclint也可以自动为你安装

### 本文解决技术要点：
+ 如何不编译工程，快速生成compile_commands.json
+ 如何对ios的壳工程里面的developer pod实现pre-commit hook检查

# 背景
oclint可以用于对Objc和C++代码进行代码规范性检查，但是一般情况下需要对整个工程进行一次编译，把生成的compile_commands.json文件输入给oclint进行代码检查。流程如下：
![image](https://user-images.githubusercontent.com/8058245/162578314-2b5d6f81-17a0-495c-8519-64a65fb89f50.png)

我们希望在git push代码的时候就带上oclint的检查，防止把不规范的代码推送到远端。
![image](https://user-images.githubusercontent.com/8058245/162578324-55c05161-c85e-4eb7-ae48-f65926e8b26d.png)
## 什么是compile_commands.json:
该文件其实是描述了Xcode编译每个单独的m文件或者swift文件所使用的具体编译参数，其生成方式如下：

```xcodebuild -scheme TestClang -sdk "iphonesimulator" -arch x86_64 | xcpretty -r json-compilation-database -o compile_commands.json```

 文件格式如下：
![image](https://user-images.githubusercontent.com/8058245/162578331-3b649434-550f-487e-80e1-7dc8d202cc96.png)
 这是一个json格式的数组，里面是一个【command，file，directory】的三元组，command描述了Xcode用于【file】的那些编译命令
 
 ## 问题：
 这里有一个非常明显的问题，就是每次运行oclint都需要拿到一个项目完整的compile_commands.json文件，这一步实在是太慢了，不可能在每次push代码的时候都去等编译工程，然后生成这样一个compile_commands.json。
 
 # 解决方案
 ## 构造compile_commands
 可以看到整个事情最关键的地方就是如何快速生成compile_commands.json，并且里面的file只有我们自己提交的文件就更好了，于是开始了全面构造compile_commands.json之旅。

一个m文件要编译通过，其实最关键的有以下几点：
1. 头文件的搜索路径
2. 预编译头文件路径
3. 系统头文件路径
4. framewwork搜索路径
5. 其它编译参数

### 导出Xcode的工程配置
```xcodebuild -json  -configuration Debug -showBuildSettings -project <ProjectName>```

 得到的结果大致如下：
![image](https://user-images.githubusercontent.com/8058245/162578339-0894d244-a0f8-46fc-9126-156daae89746.png)
 里面的HEADER_SEARCH_PATHS记录了头文件的搜索路径，当然还有其它一些有用的选项，例如Framework的搜索路径，预编译头文件路径等。

通过去解析该文件，可以自己生成一个compile_commands.json文件，大约1秒搞定···。流程如下：
![image](https://user-images.githubusercontent.com/8058245/162578351-4a551bee-7e8c-4e92-a8dd-47fd70c320bc.png)

## 安装pre-commit hooks
这一步看似简单，实际上坑还是很多的。

本文要使用的pre-commit ：

https://pre-commit.com/ 其具体使用见官网，本文将使用如下hook：

```
fail_fast: false
repos:
  - repo: local
    hooks:
      - id: local-run-pre-commit
        name: oclint
        language: system
        entry: sh {0}/hooks/fast-oclint.sh
        pass_filenames: false
        files: '^.*\.(h|cpp|cc|m|mm)'
```

即在代码提交的时候执行fast.oclint.sh这个脚本



大部分ios的工程其实都是这样一个结构：
![image](https://user-images.githubusercontent.com/8058245/162578360-69015255-e42c-4554-90ae-307c60c84801.png)

由于devpod仓库里面只有代码，没有任何编译选项，所以我们需要在某个步骤，把主工程和devpod子仓库关联起来，这个时机其实就是pod install的时候。
![image](https://user-images.githubusercontent.com/8058245/162578366-f820c772-87e2-45df-bd58-76c030a0a960.png)


其中很关键的一步是fast-oclint的安装，由于该脚本实际会调用main.py并且传入工程的绝对路径，所以每个人机器路径都是不一样的，这样就会产生一个严重的问题，解决方案要么把pre-commit-config.yaml直接gitignore掉，要么把fast-oclint.sh放到git找不到的位置，本文采用了后者，直接把fast-oclint.sh放到pre-commit的同级目录：
![image](https://user-images.githubusercontent.com/8058245/162578374-c62df78a-08e7-4af9-89f6-f2ee7208ff54.png)



# 代码分锅
oclint到这里为止，虽然实现了只对git提交的文件进行检查，但是还是不够精细，无法区分出哪些问题是本次提交引起的，所以，还需要提供一个“分锅”的功能，找出本次git commit产生的有问题的地方。
![image](https://user-images.githubusercontent.com/8058245/162578379-2d12e844-349f-476a-aee7-22c1d985c791.png)

到这里，主要问题就算基本解决了
