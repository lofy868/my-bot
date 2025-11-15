# ==============================
# part_2_ranks_system.py
# نظام الرتب والصلاحيات - عربي
# ==============================

class RanksSystem:
    def __init__(self, database):
        self.db = database
        self.ranks_hierarchy = {
            'member': 0,      # عضو عادي
            'vip': 1,         # مميز
            'admin': 2,       # أدمن
            'manager': 3,     # مدير
            'creator': 4,     # منشئ
            'owner': 5,       # مالك
            'main_owner': 6,  # مالك أساسي
            'dev': 7          # مطور
        }
    
    def get_rank_level(self, rank: str) -> int:
        """الحصول على مستوى الرتبة"""
        return self.ranks_hierarchy.get(rank, 0)
    
    def can_promote(self, promoter_rank: str, target_rank: str) -> bool:
        """التحقق إذا كان يمكن الترقية"""
        promoter_level = self.get_rank_level(promoter_rank)
        target_level = self.get_rank_level(target_rank)
        return promoter_level > target_level
    
    def get_rank_name_arabic(self, rank: str) -> str:
        """الحصول على اسم الرتبة بالعربي"""
        rank_names = {
            'member': 'عضو',
            'vip': 'مميز', 
            'admin': 'أدمن',
            'manager': 'مدير',
            'creator': 'منشئ',
            'owner': 'مالك',
            'main_owner': 'مالك أساسي',
            'dev': 'مطور'
        }
        return rank_names.get(rank, 'عضو')
    
    def promote_user(self, promoter_id: int, target_id: int, chat_id: int, target_rank: str) -> str:
        """ترقية مستخدم مع التحقق من الصلاحيات"""
        # منع ترقية النفس
        if promoter_id == target_id:
            return "❌ لا يمكنك ترقية نفسك"
        
        # الحصول على رتبة المروج والهدف
        promoter_rank = self.db.get_user_rank(promoter_id, chat_id)
        current_target_rank = self.db.get_user_rank(target_id, chat_id)
        
        # التحقق من الصلاحيات
        if not self.can_promote(promoter_rank, target_rank):
            return f"❌ لا يمكنك رفع {self.get_rank_name_arabic(target_rank)} - تحتاج رتبة أعلى"
        
        if not self.can_promote(promoter_rank, current_target_rank):
            return f"❌ لا يمكنك تعديل رتبة {self.get_rank_name_arabic(current_target_rank)} - رتبته أعلى منك"
        
        # تنفيذ الترقية
        self.db.set_user_rank(target_id, chat_id, target_rank)
        
        promoter_name = self.get_rank_name_arabic(promoter_rank)
        target_rank_name = self.get_rank_name_arabic(target_rank)
        
        return f"✅ تم رفع المستخدم إلى {target_rank_name} بنجاح\n👤 الرافع: {promoter_name}"
    
    def demote_user(self, demoter_id: int, target_id: int, chat_id: int) -> str:
        """تنزيل مستخدم مع التحقق من الصلاحيات"""
        if demoter_id == target_id:
            return "❌ لا يمكنك تنزيل نفسك"
        
        demoter_rank = self.db.get_user_rank(demoter_id, chat_id)
        target_rank = self.db.get_user_rank(target_id, chat_id)
        
        if not self.can_promote(demoter_rank, target_rank):
            return f"❌ لا يمكنك تنزيل {self.get_rank_name_arabic(target_rank)} - رتبته أعلى منك"
        
        # تنزيل إلى رتبة عضو عادي
        self.db.set_user_rank(target_id, chat_id, 'member')
        
        return f"✅ تم تنزيل المستخدم إلى عضو عادي بنجاح"
    
    def remove_all_ranks(self, remover_id: int, target_id: int, chat_id: int) -> str:
        """إزالة جميع الرتب من مستخدم"""
        if remover_id == target_id:
            return "❌ لا يمكنك إزالة رتب نفسك"
        
        remover_rank = self.db.get_user_rank(remover_id, chat_id)
        target_rank = self.db.get_user_rank(target_id, chat_id)
        
        if not self.can_promote(remover_rank, target_rank):
            return f"❌ لا يمكنك إزالة رتب {self.get_rank_name_arabic(target_rank)} - رتبته أعلى منك"
        
        self.db.remove_user_rank(target_id, chat_id)
        return "✅ تم إزالة جميع الرتب من المستخدم بنجاح"

# لا ننشئ كائن نظام الرتب هنا - سيتم إنشاؤه في الملف الرئيسي
# ranks_system = RanksSystem(db)

print("✅ تم تحميل الجزء 2 بنجاح: نظام الرتب والصلاحيات - عربي")
