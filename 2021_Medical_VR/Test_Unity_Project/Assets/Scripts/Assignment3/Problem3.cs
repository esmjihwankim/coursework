using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Problem3 : MonoBehaviour
{
    public int m_GlobalVairable1 = 0;
    private int m_GlobalVariable2 = 1;
    // Start is called before the first frame update
    void Start()
    {
        int localVariable1 = 2;

        Debug.Log("전역변수 1과 전역변수 2의 초기값은 각각 " + m_GlobalVairable1 + ", " + m_GlobalVariable2 + "입니다");
        Debug.Log("지역변수의 초기값은 " + localVariable1 + "입니다.");
        if (m_GlobalVairable1 == -1 || m_GlobalVairable1 == 0 || m_GlobalVairable1 == 1)
            Debug.Log("전역변수1과 전역변수 2의 현재값은 각각" + m_GlobalVairable1 + ", " + m_GlobalVariable2 + "입니다");
        else
            Debug.Log("전역변수1은 -1, 0, 1의 값이 아닌 다른 값입니다");
    }

    // Update is called once per frame
    void Update()
    {

    }
}
