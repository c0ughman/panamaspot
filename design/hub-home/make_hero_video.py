import subprocess, sys, os
V=os.path.dirname(os.path.abspath(__file__)); H=os.path.expanduser("~/Downloads")
# (file, start s, length s): day -> night
SHOTS=[(f"{H}/panamasky.mp4",6,4.2),(f"{V}/dl/px-35257070/clip.mp4",4,4.2),(f"{V}/dl/px-32210910/clip.mp4",10,4.2),
       (f"{V}/dl/pb-351939/clip.mp4",12,4.2),(f"{V}/dl/px-15445919/clip.mp4",3,4.2),(f"{V}/dl/px-35257071/clip.mp4",5,4.2),
       (f"{V}/dl/pb-383097/clip.mp4",4,4.2),(f"{V}/dl/pb-346372/clip.mp4",15,4.2),(f"{H}/panamaskydusk.mp4",3,4.2),(f"{H}/panamaskydark.mp4",2,4.6)]
X=0.7
def build(w,h,crf,out):
    args=["ffmpeg","-v","error","-y"]
    for f,s,d in SHOTS: args+=["-ss",str(s),"-t",str(d),"-i",f]
    fc=[f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30,format=yuv420p,setpts=PTS-STARTPTS[v{i}]" for i in range(len(SHOTS))]
    prev="v0"; t=SHOTS[0][2]
    for i in range(1,len(SHOTS)):
        off=t-X; fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={X}:offset={off:.3f}[x{i}]"); prev=f"x{i}"; t=off+SHOTS[i][2]
    args+=["-filter_complex",";".join(fc),"-map",f"[{prev}]","-an","-c:v","libx264","-preset","slow","-crf",str(crf),"-profile:v","high","-pix_fmt","yuv420p","-movflags","+faststart",out]
    subprocess.run(args,check=True); print(out, os.path.getsize(out)//1024, "KB", round(t,1),"s")
build(1600,900,31,f"{V}/hero-900.mp4")
build(960,540,31,f"{V}/hero-540.mp4")
