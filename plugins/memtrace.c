#include <qemu-plugin.h>
#include <glib.h>
#include <stdio.h>
#include <inttypes.h>
QEMU_PLUGIN_EXPORT int qemu_plugin_version = QEMU_PLUGIN_VERSION;
static FILE *out;
static void mem_cb(unsigned int cpu, qemu_plugin_meminfo_t info, uint64_t vaddr, void *ud){
 uint64_t pc=(uint64_t)(uintptr_t)ud;
 struct qemu_plugin_hwaddr *h=qemu_plugin_get_hwaddr(info,vaddr);
 uint64_t pa=h?qemu_plugin_hwaddr_phys_addr(h):vaddr;
 int io=h?qemu_plugin_hwaddr_is_io(h):0;
 fprintf(out,"0x%08" PRIx64 ",%c,0x%08" PRIx64 ",0x%08" PRIx64 ",%u,%d\n",pc,qemu_plugin_mem_is_store(info)?'W':'R',vaddr,pa,1u<<qemu_plugin_mem_size_shift(info),io);
}
static void tb_cb(struct qemu_plugin_tb *tb, void *ud){
 size_t n=qemu_plugin_tb_n_insns(tb);
 for(size_t i=0;i<n;i++){struct qemu_plugin_insn *ins=qemu_plugin_tb_get_insn(tb,i);uint64_t pc=qemu_plugin_insn_vaddr(ins);qemu_plugin_register_vcpu_mem_cb(ins,mem_cb,QEMU_PLUGIN_CB_NO_REGS,QEMU_PLUGIN_MEM_RW,(void*)(uintptr_t)pc);}
}
static void fini(qemu_plugin_id_t id, void *p){if(out) fclose(out);}
QEMU_PLUGIN_EXPORT int qemu_plugin_install(qemu_plugin_id_t id,const qemu_info_t *info,int argc,char **argv){
 const char *path="memtrace.csv";for(int i=0;i<argc;i++)if(g_str_has_prefix(argv[i],"out="))path=argv[i]+4;
 out=fopen(path,"w");if(!out)return -1;fprintf(out,"pc,rw,vaddr,paddr,size,is_io\n");
 qemu_plugin_register_vcpu_tb_trans_cb(id,tb_cb,NULL);qemu_plugin_register_atexit_cb(id,fini,NULL);return 0;
}