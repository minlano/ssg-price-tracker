import sqlite3
import os

def check_database_schema():
    """데이터베이스 스키마 확인"""
    db_path = 'database/ssg_tracker.db'
    
    if not os.path.exists(db_path):
        print("❌ 데이터베이스 파일이 존재하지 않습니다.")
        return
    
    print("📊 데이터베이스 스키마 분석")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 목록 조회
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 총 테이블 수: {len(tables)}")
        print()
        
        for table in tables:
            table_name = table[0]
            print(f"🗂️ 테이블: {table_name}")
            
            # 테이블 스키마 조회
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("   컬럼 정보:")
            for col in columns:
                col_id, name, data_type, not_null, default_val, pk = col
                pk_text = " (PRIMARY KEY)" if pk else ""
                not_null_text = " NOT NULL" if not_null else ""
                default_text = f" DEFAULT {default_val}" if default_val else ""
                
                print(f"     - {name}: {data_type}{not_null_text}{default_text}{pk_text}")
            
            # 데이터 개수 확인
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"   📊 데이터 개수: {count}개")
            
            # 샘플 데이터 (최대 3개)
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                samples = cursor.fetchall()
                print("   📝 샘플 데이터:")
                for i, sample in enumerate(samples, 1):
                    print(f"     {i}. {dict(zip([col[1] for col in columns], sample))}")
            
            print()
        
        # 인덱스 확인
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
        indexes = cursor.fetchall()
        
        if indexes:
            print("🔍 인덱스 정보:")
            for idx in indexes:
                print(f"   - {idx[0]} (테이블: {idx[1]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_database_schema()