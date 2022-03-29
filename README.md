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
