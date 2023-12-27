Zwift Workouts Parser 
---------------------
![Logo](https://github.com/alexshpunt/zwift_workouts_parser/blob/main/.github/logo.jpg?raw=true)

Want to try a workout of some specific plan on Zwift but don't want to start the plan? Use this utility to parse any desired plan or workout straight from the https://whatsonzwift.com. 

Just feed it with an URL and it will export everything it can into .zwo files which you can import into Zwift and try them out. 

Requirements
------------
Python3 [Official site](https://www.python.org/downloads/windows/) / [Microsoft Store](https://apps.microsoft.com/detail/9PJPW5LDXLZ5?hl=en-US&gl=US) 

Powershell [Microsoft's Guide](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows?view=powershell-7.4)


Installation
------------
```
python3 -m pip install --upgrade pip
```

```
pip install zwift-workouts-parser
```

Usage 
------------
Launch Powershell and execute this command: 

```
$zwift_workouts_parser = $(python3 -c "import zwift_parser as _; print (' '.join(_.__path__) + '\zwift_parser.py')")
```

Then we need to set our destination folder, where all the workouts will be stored: 

```
$zwift_workouts_folder = "C:\Users\%USERNAME%\Downloads\ZwiftWorkouts"
```

But you can choose any arbitrary path for that. 

Once it's done, you are ready to download the workouts, copy this command to the Powershell window, but don't execute it yet!

```
python3 $zwift_workouts_parser -ed $zwift_workouts_folder
```

Now you can specify all the workout urls you would like to download, separated by a space. 

So this what it looks like for a single workout: 

```
python3 $zwift_workouts_parser -ed $zwift_workouts_folder https://whatsonzwift.com/workouts/gravel-grinder`
```

And for multiple workouts: 

```
python3 $zwift_workouts_parser -ed $zwift_workouts_folder https://whatsonzwift.com/workouts/gravel-grinder https://whatsonzwift.com/workouts/30-60-minutes-to-burn https://whatsonzwift.com/workouts/climbing`
```

Once everything is downloaded, you can now put your selected workouts to Zwift workouts folder, usually it's located by this path:

C:\Users\%USERNAME%\Documents\Zwift\Workouts\%SOME_ARBITRARY_NUMBER%`.

Hopefully you will find this utility useful! 
