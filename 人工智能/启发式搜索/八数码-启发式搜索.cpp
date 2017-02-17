#include <iostream>
#include <algorithm>
#include <string>
#include <vector>
#include <queue>
#include <math.h>

using namespace std;

struct Node{
	int state[3][3];//该节点的状态
	int x,y;//记录空位置的xy坐标
	int h,g;//f(n) = g(n) + h(n)
	int Hash;//该节点的哈希值
	bool operator<(const Node N)const{
		if(h==N.h)
			return g>N.g;
		else 
			return h>N.h;
	}
	bool isRightState(){
		if(x>=0&&x<=2&&y>=0&&y<=2)
			return true;
		else 
			return false;
	}
}s,u,v,tt;

int HASH[9] = {1,1,2,6,24,120,720,5040,40320};
int destination = 322560;
/*
destination state:
	1 2 3
	4 5 6
	7 8 0
*/
int vis[400000];
int pre[400000];

int way[4][2] = {{0,1},{0,-1},{1,0},{-1,0}};

int get_hash(Node tmp){ //得到当前状态HASH值
	int a[9],k=0;
	for(int i = 0 ; i < 3 ; ++i)
		for(int j = 0 ; j < 3 ; ++j)
			a[k++]=tmp.state[i][j];
	int res = 0;
	for(int i = 0 ; i < 9 ; ++i){
		int k = 0;
		for(int j = 0 ; j < i ; ++j)
			if(a[j]>a[i])
				k++;
		res+=HASH[i]*k;
	}
	return res;
}

bool isok(Node tmp){ //判断是否有解
	int a[9],k=0;
	for(int i = 0 ; i < 3 ; ++i)
		for(int j = 0 ; j < 3 ; ++j)
			a[k++]=tmp.state[i][j];
	int sum = 0;
	for(int i = 0 ; i < 9 ; ++i)
		for(int j = i+1 ; j < 9 ; ++j)
			if(a[j]&&a[i]&&a[i]>a[j])
				sum++;
	return !(sum&1);
}

int get_h(Node tmp){ //得到h值
	int ans = 0;
	for(int i = 0 ; i < 3 ; ++i)
		for(int j = 0 ; j < 3 ; ++j)
			if(tmp.state[i][j])
				ans+=abs(i-(tmp.state[i][j]-1)/3)+abs(j-(tmp.state[i][j]-1)%3);
	return ans;
}

void astar(){
	priority_queue<Node> que;
	que.push(s);
	while (!que.empty()) {
		u = que.top();
		que.pop();
		for(int i = 0 ; i < 4 ; ++i){
			v = u;
			v.x+=way[i][0];
			v.y+=way[i][1];
			if(v.isRightState()){
				swap(v.state[v.x][v.y], v.state[u.x][u.y]);
				v.Hash=get_hash(v);
				if(vis[v.Hash]==-1&&isok(v)){
					vis[v.Hash]=i;
					v.g++;
					pre[v.Hash]=u.Hash;
					v.h=get_h(v);
					que.push(v);
				}
				if(v.Hash==destination)
					return ;
			}
		}
	}
}

void print(){  
	string ans;  
	ans.clear();  
	int nxt=destination;  
	while(pre[nxt]!=-1){  //从终点往起点找路径  
		switch(vis[nxt]){   //四个方向对应  
		case 0:ans+='r';break;  
		case 1:ans+='l';break;  
		case 2:ans+='d';break;  
		case 3:ans+='u';break;  
		}  
		nxt=pre[nxt];     
	}  
	for(int i=ans.size()-1;i>=0;i--)  
		putchar(ans[i]);  
	puts("");  
}  

int main(int argc, char *argv[]) {
	cout<<"input start state:"<<endl;
	Node N;
	char str[50];
	while(gets(str)!=NULL){
		int k = 0;
		memset(vis,-1,sizeof(vis));
		memset(pre,-1,sizeof(pre));
		for(int i = 0 ; i < 3 ; ++i){
			for(int j = 0 ; j < 3 ; ++j){
				if((str[k]<='9'&&str[k]>='0')||str[k]=='x'){
					if(str[k]=='x'){
						s.state[i][j]=0;
						s.x=i;
						s.y=j;
					}
					else
						s.state[i][j]=str[k]-'0';
				}
				else
				 	j--;
				k++;
			}
		}
		if(!isok(s)){
			cout<<"can't do it"<<endl;
			continue;
		}
		s.Hash = get_hash(s);
		if(s.Hash == destination){
			puts(" ");
			continue;
		}
		vis[s.Hash] = -2;
		s.g = 0;
		s.h = get_h(s);
		astar();
		print();
	}
	return 0;
}
