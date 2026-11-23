#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;
int NS,NP;vector<u64> polys;
struct Agg{long long n=0;vector<u64> sols;};
static inline int cnt(u64 s,bool&valid){
  u64 cov=0;int c=0;
  for(int i=0;i<NP;i++){ if((s&polys[i])==polys[i]){cov|=polys[i];c++;} }
  valid=((s&~cov)==0);return c;
}
int main(int argc,char**argv){
  int maxRel=atoi(argv[1]),maxAdd=atoi(argv[2]),maxRem=atoi(argv[3]);
  scanf("%d %d",&NS,&NP);polys.resize(NP);for(auto&p:polys)scanf("%llu",&p);
  int nst;scanf("%d",&nst);
  for(int si=0;si<nst;si++){
    u64 st;scanf("%llu",&st);
    bool v0;int c0=cnt(st,v0);
    vector<int> P,E;for(int i=0;i<NS;i++){if(st>>i&1)P.push_back(i);else E.push_back(i);}
    // mode 0 relocate,1 add,2 remove
    map<tuple<int,int,int>,Agg> agg;
    auto record=[&](int mode,int k,u64 s){
      bool v;int c=cnt(s,v);if(!v||c==0||c==c0)return;
      auto&a=agg[make_tuple(mode,k,c)];a.n++;if(a.sols.size()<40)a.sols.push_back(s);
    };
    // helper combos
    function<void(const vector<int>&,int,int,u64,vector<u64>&)> comb=[&](const vector<int>&V,int k,int start,u64 acc,vector<u64>&out){
      if(k==0){out.push_back(acc);return;}
      for(int i=start;i<(int)V.size();i++)comb(V,k-1,i+1,acc|(1ULL<<V[i]),out);
    };
    for(int k=1;k<=max(maxRel,max(maxAdd,maxRem));k++){
      vector<u64> rem,add;
      if(k<=maxRel||k<=maxRem)comb(P,k,0,0,rem);
      if(k<=maxRel||k<=maxAdd)comb(E,k,0,0,add);
      if(k<=maxRem)for(u64 r:rem)record(2,k,st&~r);
      if(k<=maxAdd)for(u64 a:add)record(1,k,st|a);
      if(k<=maxRel)for(u64 r:rem){u64 b=st&~r;for(u64 a:add)record(0,k,b|a);}
    }
    for(auto&kv:agg){
      auto [mode,k,c]=kv.first;
      printf("%d %d %d %d %lld %d",si,mode,k,c,kv.second.n,(int)kv.second.sols.size());
      for(u64 s:kv.second.sols)printf(" %llu",s);
      printf("\n");
    }
  }
}
